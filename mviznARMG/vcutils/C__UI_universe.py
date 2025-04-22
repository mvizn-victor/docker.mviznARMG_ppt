#version: 1.0.3
#1.0.1
#  if fromjupyter don't run
#1.0.2
#  customkeypress
#  render after pushpage, poppage
#  click textbox,textarea clicked_obj.cursor_index = len(clicked_obj.text)
#1.0.3
#  fix image canvas assign size mismatch

from pyquery import PyQuery as pq
import cv2
import time
import json
import os
import numpy as np
import traceback
import threading
import xml.etree.ElementTree as ET
from io import StringIO
import re

# ----------------------
# Helper Functions
# ----------------------

def get_error_string(e):
    sio = StringIO()
    print("An exception occurred:", e, file=sio)
    print("\nStack trace:", file=sio)
    print(traceback.format_exc(), file=sio)
    return sio.getvalue()

def makedirsf(f):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    return f

def run_in_background(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

def parse_spacing(spacing_str, container_width, container_height, universe_width, universe_height):
    tokens = spacing_str.split()
    if len(tokens) == 0:
        return (0, 0, 0, 0)
    elif len(tokens) == 1:
        left = parse_horizontal_token(tokens[0], container_width, container_height, universe_width, universe_height)
        top = parse_vertical_token(tokens[0], container_width, container_height, universe_width, universe_height)
        return (left, top, left, top)
    elif len(tokens) == 2:
        left = parse_horizontal_token(tokens[0], container_width, container_height, universe_width, universe_height)
        top = parse_vertical_token(tokens[1], container_width, container_height, universe_width, universe_height)
        return (left, top, left, top)
    elif len(tokens) == 3:
        left = parse_horizontal_token(tokens[0], container_width, container_height, universe_width, universe_height)
        top = parse_vertical_token(tokens[1], container_width, container_height, universe_width, universe_height)
        right = parse_horizontal_token(tokens[2], container_width, container_height, universe_width, universe_height)
        bottom = top
        return (left, top, right, bottom)
    else:
        left = parse_horizontal_token(tokens[0], container_width, container_height, universe_width, universe_height)
        top = parse_vertical_token(tokens[1], container_width, container_height, universe_width, universe_height)
        right = parse_horizontal_token(tokens[2], container_width, container_height, universe_width, universe_height)
        bottom = parse_vertical_token(tokens[3], container_width, container_height, universe_width, universe_height)
        return (left, top, right, bottom)

def parse_horizontal_token(token, container_width, container_height, universe_width, universe_height):
    if token.endswith("vh"):
        return int(float(token[:-2]) * universe_height / 100)
    elif token.endswith("vw"):
        return int(float(token[:-2]) * universe_width / 100)
    elif token.endswith("vmin"):
        return int(float(token[:-4]) * min(universe_width, universe_height) / 100)
    elif token.endswith("%"):
        return int(float(token[:-1]) * container_width / 100)
    else:
        return 0

def parse_vertical_token(token, container_width, container_height, universe_width, universe_height):
    if token.endswith("vh"):
        return int(float(token[:-2]) * universe_height / 100)
    elif token.endswith("vw"):
        return int(float(token[:-2]) * universe_width / 100)
    elif token.endswith("vmin"):
        return int(float(token[:-4]) * min(universe_width, universe_height) / 100)
    elif token.endswith("%"):
        return int(float(token[:-1]) * container_height / 100)
    else:
        return 0

def get_multiline_text_size(text, font, fontScale, thickness):
    lines = text.split('\n')
    max_width = 0
    total_height = 0
    for line in lines:
        (w, h), baseline = cv2.getTextSize(line, font, fontScale, thickness)
        max_width = max(max_width, w)
        total_height += h + baseline
    return max_width, total_height

def put_text_multiline(img, text, org, font, fontScale, color, thickness=1, lineType=cv2.LINE_AA, hjust="left"):
    lines = text.split('\n')
    x, y = org
    max_width, _ = get_multiline_text_size(text, font, fontScale, thickness)
    for line in lines:
        (w, h), baseline = cv2.getTextSize(line, font, fontScale, thickness)
        if hjust == "center":
            line_x = x + (max_width - w) // 2
        elif hjust == "right":
            line_x = x + (max_width - w)
        else:
            line_x = x
        cv2.putText(img, line, (line_x, y + h), font, fontScale, color, thickness, lineType)
        y += h + baseline

def compute_text_origin(bounding_box, text, font, scale, thickness, hjust='left', vjust='top', padding=5):
    x1, y1, x2, y2 = bounding_box
    allocated_width = x2 - x1
    allocated_height = y2 - y1
    text_width, text_height = get_multiline_text_size(text, font, scale, thickness)
    if hjust == 'center':
        text_x = x1 + (allocated_width - text_width) // 2
    elif hjust == 'right':
        text_x = x2 - text_width - padding
    else:
        text_x = x1 + padding
    if vjust == 'center':
        text_y = y1 + (allocated_height - text_height) // 2
    elif vjust == 'bottom':
        text_y = y2 - text_height - padding
    else:
        text_y = y1 + padding
    return (text_x, text_y)

def padded_text(text):
    return ' ' + text + ' '

# ----------------------
# Event Classes
# ----------------------

class C__mouseclickevent:
    def __init__(self, universe, clicked_obj, x, y, localx, localy, otherparams=None):
        self.universe = universe
        self.clicked_obj = clicked_obj
        self.x = x
        self.y = y
        self.localx = localx
        self.localy = localy
        self.otherparams = otherparams if otherparams is not None else {}

class C__keypressevent:
    def __init__(self, universe, clicked_obj, k, otherparams=None):
        self.universe = universe
        self.clicked_obj = clicked_obj
        self.k = k
        self.otherparams = otherparams if otherparams is not None else {}

# ----------------------
# Base UI Object Class
# ----------------------

class C__UI_object:
    next_element_index = 0
    def __init__(self, universe, parent, xml_element):
        self.universe = universe
        self.parent = parent
        self.objecttype = xml_element.tag.lower()
        self.children = []
        self.props = xml_element.attrib.copy()
        if self.objecttype in ["textbox", "button", "textarea", "menu1", "menu2"]:
            self.props.setdefault("outline", "true")
        else:
            self.props.setdefault("outline", "false")
        if "onclick" in self.props:
            onclick_code = self.props["onclick"]
            def onclick_handler(event, code=onclick_code):
                try:
                    universe.local_env['event'] = event
                    universe.local_env['universe'] = universe
                except:
                    universe.local_env = {'event': event, 'universe': universe}
                try:
                    exec(code, globals(), universe.local_env)
                except Exception as e:
                    print("Error in onclick exec:", e)
            self.onclick = onclick_handler
        if "onkeypress" in self.props:
            onkeypress_code = self.props["onkeypress"]
            def onkeypress_handler(event, code=onkeypress_code):
                try:
                    universe.local_env['event'] = event
                    universe.local_env['universe'] = universe
                except:
                    universe.local_env = {'event': event, 'universe': universe}
                try:
                    exec(code, globals(), universe.local_env)
                except Exception as e:
                    print("Error in onkeypress exec:", e)
            self.onkeypress = onkeypress_handler
        if self.objecttype in ["textbox", "label"]:
            self.props.setdefault("vjust", "center")
        self.text = self.props.get('text', '')
        self.id = self.props.get('id', None)
        self.weight = float(self.props.get('weight', 1))
        self.elementindex = C__UI_object.next_element_index
        C__UI_object.next_element_index += 1
        if self.objecttype in ["menu1", "menu2"]:
            self.zindex = int(self.props.get("zindex", 1000))
        else:
            self.zindex = int(self.props.get("zindex", 0))
        if self.objecttype in ['menu1', 'menu2']:
            self.expanded = False
        if self.objecttype in ['textbox', 'textarea']:
            self.focused = False
            self.cursor_index = len(self.text)
            self.sel_start = None
            self.sel_end = None
        self.props.setdefault("backgroundcolor", self.universe.backgroundcolor)
        self.props.setdefault("fontcolor", self.universe.fontcolor)
        self.props.setdefault("outlinecolor", self.universe.outlinecolor)
        for child in xml_element:
            child_obj = C__UI_object(universe, self, child)
            self.children.append(child_obj)

    def _parse_color(self, color):
        if isinstance(color, (tuple, list)):
            return tuple(color)
        elif isinstance(color, str):
            if color.startswith('#') and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    return (b, g, r)
                except Exception as e:
                    print("Error parsing hex color:", e)
                    return (0, 0, 0)
            mapping = dict(zip(self.universe.rainbowbgrname, self.universe.rainbowbgr))
            return mapping.get(color.lower(), (0, 0, 0))
        else:
            return (0, 0, 0)

    def parse_dimension(self, dim_str, total_reference):
        try:
            if dim_str.endswith("vh"):
                return int(float(dim_str[:-2]) * self.universe.height / 100)
            elif dim_str.endswith("vw"):
                return int(float(dim_str[:-2]) * self.universe.width / 100)
            elif dim_str.endswith("vmin"):
                return int(float(dim_str[:-4]) * min(self.universe.width, self.universe.height) / 100)
            elif dim_str.endswith("%"):
                return int(float(dim_str[:-1]) * total_reference / 100)
            else:
                return int(dim_str)
        except:
            return 0

    def do_layout(self, x, y, width, height):
        margin_left, margin_top, margin_right, margin_bottom = (0, 0, 0, 0)
        if "margin" in self.props:
            margin_left, margin_top, margin_right, margin_bottom = parse_spacing(self.props["margin"], width, height, self.universe.width, self.universe.height)
        content_x = x + margin_left
        content_y = y + margin_top
        content_width = max(width - margin_left - margin_right, 0)
        content_height = max(height - margin_top - margin_bottom, 0)
        self.bounding_box = (content_x, content_y, content_x + content_width, content_y + content_height)
        padding_left, padding_top, padding_right, padding_bottom = (0, 0, 0, 0)
        if "padding" in self.props:
            padding_left, padding_top, padding_right, padding_bottom = parse_spacing(self.props["padding"], content_width, content_height, self.universe.width, self.universe.height)
        inner_x = content_x + padding_left
        inner_y = content_y + padding_top
        inner_width = max(content_width - padding_left - padding_right, 0)
        inner_height = max(content_height - padding_top - padding_bottom, 0)
        mfh_str = self.props.get('maxfontheight', None)
        if mfh_str:
            self.maxfontheight = min(height, self.parse_dimension(mfh_str, height))
        else:
            self.maxfontheight = min(height, self.parse_dimension('5vh', height))

        if self.objecttype == "menubar":
            H = height
            current_x = x
            for child in self.children:
                font = cv2.FONT_HERSHEY_SIMPLEX
                base_text_size, _ = cv2.getTextSize(padded_text(child.text), font, 1, 2)
                s = (max(min(H, self.maxfontheight) - 10, 0) / base_text_size[1]) if base_text_size[1] > 0 else 1.0
                child.font_scale = s
                text_size, _ = cv2.getTextSize(padded_text(child.text), font, s, 2)
                child.fixed_width = text_size[0]
                child.fixed_height = H
                child.maxfontheight = self.maxfontheight
                child.do_layout(current_x, y, child.fixed_width, child.fixed_height)
                current_x += child.fixed_width
            self.bounding_box = (x, y, current_x, y + H)
            return
        if self.objecttype == 'rows':
            fixed_total = 0
            flexible = []
            for child in self.children:
                h_str = child.props.get('height', None)
                if h_str:
                    fixed_height = child.parse_dimension(h_str, inner_height)
                    child.fixed_height = fixed_height
                    fixed_total += fixed_height
                else:
                    flexible.append(child)
            remaining = max(inner_height - fixed_total, 0)
            total_weight = sum(child.weight for child in flexible) if flexible else 0
            current_y = inner_y
            for child in self.children:
                if hasattr(child, 'fixed_height'):
                    child_height = child.fixed_height
                else:
                    child_height = int(remaining * (child.weight / total_weight)) if total_weight > 0 else int(remaining / len(flexible))
                child.do_layout(inner_x, current_y, inner_width, child_height)
                current_y += child_height
        elif self.objecttype == 'columns':
            fixed_total = 0
            flexible = []
            for child in self.children:
                w_str = child.props.get('width', None)
                if w_str:
                    fixed_width = child.parse_dimension(w_str, inner_width)
                    child.fixed_width = fixed_width
                    fixed_total += fixed_width
                else:
                    flexible.append(child)
            remaining = max(inner_width - fixed_total, 0)
            total_weight = sum(child.weight for child in flexible) if flexible else 0
            current_x = inner_x
            for child in self.children:
                if hasattr(child, 'fixed_width'):
                    child_width = child.fixed_width
                else:
                    child_width = int(remaining * (child.weight / total_weight)) if total_weight > 0 else int(remaining / len(flexible))
                child.do_layout(current_x, inner_y, child_width, inner_height)
                current_x += child_width
        else:
            pass
        if self.objecttype in ['menu1', 'menu2'] and getattr(self, 'expanded', False) and self.children:
            if self.objecttype == 'menu1':
                dropdown_x = x
                dropdown_y = y + height
            elif self.objecttype == 'menu2':
                dropdown_x = x + width
                dropdown_y = y
            max_width = width if self.parent.objecttype == 'menu1' else 0
            H = height
            for child in self.children:
                suffix = ' >' if len(child.children) > 0 else ''
                font = cv2.FONT_HERSHEY_SIMPLEX
                base_text_size, _ = cv2.getTextSize(padded_text(child.text), font, 1, 2)
                s = (max(H - 10, 0) / base_text_size[1]) if base_text_size[1] > 0 else 1.0
                child.font_scale = s
                text_size, _ = cv2.getTextSize(padded_text(child.text), font, s, 2)
                req_width = text_size[0]
                max_width = max(max_width, req_width)
                child.fixed_width = req_width
                child.fixed_height = H
            for child in self.children:
                child.fixed_width = max_width
                child.do_layout(dropdown_x, dropdown_y, max_width, child.fixed_height)
                dropdown_y += child.fixed_height


    def get_wrapped_lines(self, font, scale, thickness):
        available_width = self.bounding_box[2] - self.bounding_box[0] - 10
        lines = []

        # Preserve consecutive newlines by splitting with `\n`
        raw_lines = self.text.split('\n')

        for raw_line in raw_lines:
            if raw_line.strip() == "":
                lines.append("")  # Preserve empty lines
                continue

            words = raw_line.split(' ')
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_width, _ = cv2.getTextSize(test_line, font, scale, thickness)[0]

                if test_width > available_width:
                    if current_line:
                        lines.append(current_line)  # Store the completed line
                    current_line = word  # Start a new line with the current word
                else:
                    current_line = test_line  # Continue adding to the current line

            if current_line or raw_line == "":  
                lines.append(current_line)  # Append last line for this segment
        
        return lines

    def draw(self, canvas):
        if hasattr(self, "bounding_box"):
            x1, y1, x2, y2 = self.bounding_box
            bg_color = self._parse_color(self.props.get("backgroundcolor", self.universe.backgroundcolor))
            cv2.rectangle(canvas, (x1, y1), (x2, y2), bg_color, -1)
        if self.objecttype in ['menu1', 'menu2', 'button']:
            suffix = ' >' if (self.objecttype == "menu2" and self.children) else ''
            x1, y1, x2, y2 = self.bounding_box
            allocated_width = x2 - x1
            allocated_height = y2 - y1
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 1
            fitheight = True
            fitwidth = False if 'menu' in self.objecttype else True
            base_scale = 1.0

            base_width, base_height = get_multiline_text_size(padded_text('A'), font, base_scale, thickness)
            scale_h0 = (self.maxfontheight - 10) / base_height

            base_width, base_height = get_multiline_text_size(padded_text(self.text + suffix), font, base_scale, thickness)
            scale_h = (allocated_height - 10) / base_height if (fitheight and base_height > 0) else base_scale
            scale_w = (allocated_width - 10) / base_width if (fitwidth and base_width > 0) else base_scale

            if fitwidth:
                scale = min(scale_h0, scale_h, scale_w)
            else:
                scale = min(scale_h0, scale_h)

            thickness = int(round(scale * float(self.props.get("thickness", "1"))))
            hjust = self.props.get("hjust", "center").lower()
            vjust = self.props.get("vjust", "center").lower()
            origin = compute_text_origin(self.bounding_box, padded_text(self.text + suffix), font, scale, thickness, hjust, vjust, padding=5)
            put_text_multiline(canvas, padded_text(self.text + suffix), origin, font, scale, self._parse_color(self.props.get("fontcolor", self.universe.fontcolor)), thickness, hjust=hjust)
        elif self.objecttype in ['label','textbox']:
            suffix = ''
            x1, y1, x2, y2 = self.bounding_box
            allocated_width = x2 - x1
            allocated_height = y2 - y1
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 1
            fitheight = True
            fitwidth = False if 'menu' in self.objecttype else True

            base_scale = 1.0
            base_width, base_height = get_multiline_text_size(padded_text('A'), font, base_scale, thickness)
            scale_h0 = (self.maxfontheight - 10) / base_height

            base_width, base_height = get_multiline_text_size(padded_text(self.text), font, base_scale, thickness)
            scale_h = (allocated_height - 10) / base_height

            scale_w = (allocated_width - 10) / base_width
            scale = min(scale_h0, scale_h)


            thickness = int(round(scale * float(self.props.get("thickness", "1"))))
            hjust = self.props.get("hjust", "center").lower() if self.objecttype=="label" else "left"
            vjust = self.props.get("vjust", "center").lower()
            origin = compute_text_origin(self.bounding_box, padded_text(self.text + suffix), font, scale, thickness, hjust, vjust, padding=5)
            put_text_multiline(canvas, padded_text(self.text + suffix), origin, font, scale, self._parse_color(self.props.get("fontcolor", self.universe.fontcolor)), thickness, hjust=hjust)

            if self.objecttype == 'textbox' and self.focused:
                cursor_line_text = self.text

                prefix = cursor_line_text[:max(0, self.cursor_index)]
                (cw, ch), baseline = cv2.getTextSize(' '+prefix, font, scale, thickness)
                line_height = ch + baseline
                cursor_x = x1 + 5 + cw
                cursor_y = (y1+y2-ch)//2 
                if int(time.time()*2) % 2 == 0:
                    cv2.line(canvas, (cursor_x, cursor_y), (cursor_x, cursor_y + ch), self._parse_color(self.props.get("fontcolor", self.universe.fontcolor)), 2)

        elif self.objecttype in ['textarea']:
            x1, y1, x2, y2 = self.bounding_box
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 1

            base_scale = 1.0
            base_width, base_height = get_multiline_text_size(padded_text('A'), font, base_scale, thickness)
            scale_h0 = (self.maxfontheight - 10) / base_height

            scale = scale_h0


            lines = self.get_wrapped_lines(font, scale, thickness)
            cursor_line_text = ""
            cursor_line_index = 0
            total_chars = 0
            line_height = 0
            y_cursor = y1 + 5
            found=0
            for i, line in enumerate(lines):
                (w, h), baseline = cv2.getTextSize(line, font, scale, thickness)
                line_height = h + baseline
                cv2.putText(canvas, line, (x1+5, y_cursor + h), font, scale, self._parse_color(self.props.get("fontcolor", self.universe.fontcolor)), thickness, cv2.LINE_AA)
                if total_chars + len(line) >= self.cursor_index and not found:
                    cursor_line_text = line
                    cursor_line_index = i
                    found=1
                if not found:
                    total_chars += len(line) + 1
                y_cursor += line_height
            if self.focused:
                prefix = cursor_line_text[:max(0, self.cursor_index - total_chars)]
                (cw, ch), _ = cv2.getTextSize(prefix, font, scale, thickness)
                cursor_x = x1 + 5 + cw
                cursor_y = y1 + 5 + cursor_line_index * line_height
                if int(time.time()*2) % 2 == 0:
                    cv2.line(canvas, (cursor_x, cursor_y), (cursor_x, cursor_y + ch), self._parse_color(self.props.get("fontcolor", self.universe.fontcolor)), 2)
        elif self.objecttype == 'image':
            x1, y1, x2, y2 = self.bounding_box
            allocated_width = x2 - x1
            allocated_height = y2 - y1
            cv2.rectangle(canvas, (x1, y1), (x2, y2), self._parse_color(self.props.get("backgroundcolor", self.universe.backgroundcolor)), -1)
            if hasattr(self, 'im') and self.im is not None:
                orig_h, orig_w = self.im.shape[:2]
                fitheight = self.props.get("fitheight", "true").lower() == "true"
                fitwidth = self.props.get("fitwidth", "true").lower() == "true"
                if fitheight and fitwidth:
                    scale_factor = min(allocated_width/orig_w, allocated_height/orig_h)
                elif fitheight:
                    scale_factor = allocated_height/orig_h
                elif fitwidth:
                    scale_factor = allocated_width/orig_w
                else:
                    scale_factor = 1.0
                new_w = int(orig_w * scale_factor)
                new_h = int(orig_h * scale_factor)
                resized = cv2.resize(self.im, (new_w, new_h))
                hjust = self.props.get("hjust", "center").lower()
                vjust = self.props.get("vjust", "center").lower()
                if hjust == "left":
                    offset_x = x1
                elif hjust == "right":
                    offset_x = x2 - new_w
                else:
                    offset_x = x1 + (allocated_width - new_w)//2
                if vjust == "top":
                    offset_y = y1
                elif vjust == "bottom":
                    offset_y = y2 - new_h
                else:
                    offset_y = y1 + (allocated_height - new_h)//2

                # Ensure resized image fits within canvas dimensions
                end_y = min(offset_y + new_h, canvas.shape[0])
                end_x = min(offset_x + new_w, canvas.shape[1])
                start_y = max(offset_y, 0)
                start_x = max(offset_x, 0)

                # Adjust resized image to match the clipping
                resized_cropped = resized[start_y - offset_y:end_y - offset_y, start_x - offset_x:end_x - offset_x]

                canvas[start_y:end_y, start_x:end_x] = resized_cropped

                #canvas[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = resized
                self.offset_x = offset_x
                self.offset_y = offset_y
                self.new_w = new_w
                self.new_h = new_h
                bordercolor = self.props.get("bordercolor", self.universe.bordercolor)
                borderthickness = int(self.props.get("borderthickness", self.universe.borderthickness))
                if borderthickness > 0:
                    cv2.rectangle(canvas, (offset_x, offset_y), (offset_x+new_w, offset_y+new_h), self._parse_color(bordercolor), borderthickness)
            else:
                cv2.rectangle(canvas, (x1, y1), (x2, y2), self._parse_color(self.props.get("outlinecolor", self.universe.outlinecolor)), 1)
        elif self.objecttype == "checkbox":
            x1, y1, x2, y2 = self.bounding_box
            side = min(x2-x1, y2-y1)
            bg_color = self._parse_color(self.props.get("backgroundcolor", self.universe.backgroundcolor))
            cv2.rectangle(canvas, (x1, y1), (x1+side, y1+side), bg_color, -1)
            if self.props.get("outline", "false").lower() == "true":
                cv2.rectangle(canvas, (x1, y1), (x1+side, y1+side), self._parse_color(self.props.get("outlinecolor", self.universe.outlinecolor)), 2)
            if self.props.get("value", "false").lower() == "true":
                cv2.line(canvas, (x1, y1), (x1+side, y1+side), (0,255,0), 2)
                cv2.line(canvas, (x1, y1+side), (x1+side, y1), (0,255,0), 2)
        else:
            x1, y1, x2, y2 = self.bounding_box
        if self.props.get("outline", "false").lower() == "true":
            cv2.rectangle(canvas, (x1, y1), (x2, y2), self._parse_color(self.props.get("outlinecolor", self.universe.outlinecolor)), 2)

    def collect_render_commands(self, commands):
        commands.append((self.zindex, self.elementindex, lambda canvas: self.draw(canvas)))
        if self.objecttype in ['rows', 'columns', 'menubar']:
            for child in sorted(self.children, key=lambda child: (child.zindex, child.elementindex)):
                child.collect_render_commands(commands)
        elif self.objecttype in ['menu1', 'menu2'] and getattr(self, 'expanded', False):
            for child in sorted(self.children, key=lambda child: (child.zindex, child.elementindex)):
                child.collect_render_commands(commands)

# ----------------------
# UI Page Class
# ----------------------

class C__UI_page:
    def __init__(self, universe, pagekey, pagexml):
        self.universe = universe
        self.pagekey = pagekey
        self.pagexml = pagexml
        self.root = None
        self.load_pagexml(pagexml)
    def load_pagexml(self, pagexml):
        root_elem = ET.fromstring(pagexml)
        self.root = C__UI_object(self.universe, None, root_elem)
        self.root.do_layout(0, 0, self.universe.width, self.universe.height)
    def getElementById(self, elid):
        return self._search_by_id(self.root, elid)
    def _search_by_id(self, obj, elid):
        if obj is None:
            return None
        if obj.id == elid:
            return obj
        for child in obj.children:
            res = self._search_by_id(child, elid)
            if res:
                return res
        return None
    def render(self):
        canvas = np.zeros((self.universe.height, self.universe.width, 3), dtype=np.uint8)
        canvas[:] = self.universe._parse_color(self.universe.backgroundcolor)
        self.root.do_layout(0, 0, self.universe.width, self.universe.height)
        commands = []
        self.root.collect_render_commands(commands)
        commands.sort(key=lambda cmd: (cmd[0], cmd[1]))
        for _, _, draw_func in commands:
            draw_func(canvas)
        return canvas

# ----------------------
# UI Universe Class
# ----------------------

class C__UI_universe:
    def __init__(self, fd, app=None, **props):
        self.__dict__.update(props)
        self.width = props.get("width", 1920)
        self.height = props.get("height", 1080)
        self.startpage = props.get("startpage", "demo")
        self.backgroundcolor = props.get("backgroundcolor", "black")
        self.fontcolor = props.get("fontcolor", "white")
        self.outlinecolor = props.get("outlinecolor", "white")
        self.bordercolor = props.get("bordercolor", "white")
        self.borderthickness = props.get("borderthickness", 0)
        self.fps = props.get("fps", 5)
        self.pagesxml = props.get("pagesxml", """<root><page id="demo"><label text="Hello World"></label></page></root>""")
        self.css = props.get("css", "")
        self.css_hard = props.get("css_hard", "")
        self.fd = fd
        self.app = app
        self.pagestack = []
        self.pushpage(self.startpage)
        self.fd.onclick = self.handleclick
        self.fd.startlistener()
        self.fd.app = self
        self.customupdate = None
        self.customkeypress = None
        self.customoncommand = None
        self.focused_widget = None

    def expand_menu_path(self, clicked_obj):
        """
        Expand all menus along the path from the clicked object to the root.
        """
        self.collapse_all_menus(self.pagestack[-1].root)
        current = clicked_obj
        for child in current.children:
            child.disable = False
        while current is not None:
            if current.objecttype in ['menu1', 'menu2'] and current.children:
                current.expanded = True
                current.disable = False
            current = current.parent
            if current:
                for child in current.children:
                    child.disable = False

    rainbowbgr = [(0, 0, 255),
                  (0, 165, 255),
                  (0, 255, 255),
                  (0, 128, 0),
                  (255, 0, 0),
                  (130, 0, 75),
                  (238, 130, 238),
                  (128, 128, 128),
                  (255, 255, 255),
                  (0, 0, 0)]
    rainbowbgrname = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "gray", "white", "black"]
    def _parse_color(self, color):
        if isinstance(color, (tuple, list)):
            return tuple(color)
        elif isinstance(color, str):
            if color.startswith('#') and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    return (b, g, r)
                except Exception as e:
                    print("Error parsing hex color:", e)
                    return (0, 0, 0)
            mapping = dict(zip(self.rainbowbgrname, self.rainbowbgr))
            return mapping.get(color.lower(), (0, 0, 0))
        else:
            return (0, 0, 0)
    def handleclick(self, fd_instance, x, y):
        print(f"UI_universe received click at: {x}, {y}")
        clicked_obj = self._find_clicked(self.pagestack[-1].root, x, y)
        if clicked_obj:
            bx1, by1, bx2, by2 = clicked_obj.bounding_box
            localx = x - bx1
            localy = y - by1
            if clicked_obj.objecttype == "image":
                cx1 = clicked_obj.offset_x
                cy1 = clicked_obj.offset_y
                cx2 = clicked_obj.offset_x + clicked_obj.new_w
                cy2 = clicked_obj.offset_y + clicked_obj.new_h
                imagex = int(round((x - cx1) / (cx2 - cx1) * clicked_obj.im.shape[1]))
                imagey = int(round((y - cy1) / (cy2 - cy1) * clicked_obj.im.shape[0]))
                event = C__mouseclickevent(self, clicked_obj, x, y, localx, localy, otherparams={"id": clicked_obj.id, "imagexy": (imagex, imagey)})
            else:
                event = C__mouseclickevent(self, clicked_obj, x, y, localx, localy, otherparams={"id": clicked_obj.id})
            print(f"Firing onclick for object id={clicked_obj.id}, type={clicked_obj.objecttype}")
            if hasattr(clicked_obj, "onclick") and callable(clicked_obj.onclick):
                clicked_obj.onclick(event)
            if clicked_obj.objecttype == "checkbox":
                current_val = clicked_obj.props.get("value", "false").lower()
                new_val = "true" if current_val == "false" else "false"
                clicked_obj.props["value"] = new_val
                print(f"Checkbox {clicked_obj.id} toggled to {new_val}")
            if clicked_obj.objecttype in ["textbox", "textarea"]:
                self.focused_widget = clicked_obj
                self._clear_focus(self.pagestack[-1].root, except_obj=clicked_obj)
                clicked_obj.focused = True
                clicked_obj.cursor_index = len(clicked_obj.text)
            else:
                self.focused_widget = None
                if clicked_obj.objecttype not in ['menu1', 'menu2']:
                    self.collapse_all_menus(self.pagestack[-1].root)
            if clicked_obj.objecttype in ['menu1', 'menu2'] and clicked_obj.children:
                self.expand_menu_path(clicked_obj)
    def _clear_focus(self, obj, except_obj=None):
        if obj.objecttype in ["textbox", "textarea"]:
            if obj != except_obj:
                obj.focused = False
        for child in obj.children:
            self._clear_focus(child, except_obj)
    def _collect_clickable(self, obj, clickable):
        if hasattr(obj, "bounding_box"):
            clickable.append(obj)
        for child in obj.children:
            self._collect_clickable(child, clickable)
    def _find_clicked(self, root, x, y):
        clickable = []
        self._collect_clickable(root, clickable)
        clickable.sort(key=lambda o: (o.zindex, o.elementindex), reverse=True)
        for obj in clickable:
            if obj.__dict__.get('disable', False):
                continue
            x1, y1, x2, y2 = obj.bounding_box
            if x1 <= x <= x2 and y1 <= y <= y2:
                return obj
        return None
    def handlekeypress(self, k):
        if k != -1:
            print("Key pressed:", k)
            if self.focused_widget and self.focused_widget.objecttype in ['textbox', 'textarea']:
                widget = self.focused_widget
                if k in [8]:
                    if widget.cursor_index > 0:
                        widget.text = widget.text[:widget.cursor_index-1] + widget.text[widget.cursor_index:]
                        widget.cursor_index -= 1
                elif k in [127]:
                    if widget.cursor_index < len(widget.text):
                        widget.text = widget.text[:widget.cursor_index] + widget.text[widget.cursor_index+1:]
                elif k == 37:
                    widget.cursor_index = max(0, widget.cursor_index - 1)
                elif k in [38,40]:
                    pass
                elif k == 39:
                    widget.cursor_index = min(len(widget.text), widget.cursor_index + 1)
                elif k == 13 and widget.objecttype == 'textbox' or k == 27:
                    widget.focused = False
                else:
                    try:
                        if k==13:
                            char = '\n'
                            print("HERE")
                        else:
                            char = chr(k)
                        widget.text = widget.text[:widget.cursor_index] + char + widget.text[widget.cursor_index:]
                        print(widget.text)
                        widget.cursor_index += 1
                    except Exception as e:
                        print("Key processing error:", e)
            else:
                if self.customkeypress:
                    self.customkeypress(self,k)
    def collapse_all_menus(self, obj):
        if obj.objecttype in ['menu1', 'menu2']:
            obj.expanded = False
        if obj.objecttype == 'menu2':
            obj.disable = True
        for child in obj.children:
            self.collapse_all_menus(child)
    def render(self):
        self.canvas = self.pagestack[-1].render()
        k = self.fd.imswk(self.canvas, 1)
        self.handlekeypress(k)
        return self.canvas
    def update(self):
        if self.customupdate:
            try:
                self.customupdate(self)
            except Exception as e:
                print("Error in customupdate:", e)
    def run(self):
        while True:
            startT = time.time()
            self.update()
            self.render()
            elapsed = time.time() - startT
            time.sleep(max(1/self.fps - elapsed, 0))
    def step(self):
        self.update()
        return self.canvas
    def addpagexml(self, pagekey, pagexml):
        self.dict__pagexml[pagekey] = pagexml
    def pushpage(self, pagekey):
        tmp1 = apply_css(self.pagesxml, self.css, False)
        tmp2 = apply_css(tmp1, self.css_hard, True)
        self.dict__pagexml = pagesxml_to_dict(tmp2)
        if pagekey in self.dict__pagexml:
            page = C__UI_page(self, pagekey, self.dict__pagexml[pagekey])
            self.pagestack.append(page)
        else:
            print("Page key not found:", pagekey)
    def poppage(self):
        if len(self.pagestack) > 1:
            self.pagestack.pop()
        else:
            print("Cannot pop the last page")
        self.render()
    def getElementById(self, elid):
        if self.pagestack:
            return self.pagestack[-1].getElementById(elid)
        return None

def pagesxml_to_dict(xml_string):
    tree = ET.ElementTree(ET.fromstring(xml_string))
    root = tree.getroot()
    pages = {}
    for page in root.findall("page"):
        page_id = page.get("id")
        pagexml = ''.join(ET.tostring(e, encoding='unicode', method='xml') for e in page)
        pages[page_id] = pagexml.strip()
    return pages

def apply_css(pagexml, script, hard):
    def parse_css(script):
        rules = []
        pattern = re.compile(r'([^{]+){([^}]+)}')
        for match in pattern.finditer(script):
            selectors = [s.strip() for s in match.group(1).split(',')]
            rules_str = match.group(2).strip()
            properties = {}
            for prop in rules_str.split(';'):
                prop = prop.strip()
                if not prop:
                    continue
                if ':' in prop:
                    key, value = prop.split(':', 1)
                properties[key.strip()] = value.strip()
            rules.append({'selectors': selectors, 'properties': properties})
        return rules

    doc = pq(pagexml)
    css_rules = parse_css(script)
    
    for rule in css_rules:
        for selector in rule['selectors']:
            elements = doc(selector)
            for elem in elements.items():
                for k, v in rule['properties'].items():
                    if hard or elem.attr(k) is None:
                        elem.attr(k, str(v))  # Ensure all values are converted to strings
    return doc.outer_html()


# ----------------------
# Demo XML and CSS
# ----------------------

demo_xml = """<root>
  <page id="demo">
    <rows margin="2vh">
      <menubar height="6vh" maxfontheight="4vh">
        <menu1 text="File" id="file">
            <menu2 text="open" onclick="universe.pushpage('open')">
            </menu2>
        </menu1>
        <menu1 text="Edit" id="edit">
          <menu2 text="sub1"><menu2 text="sub2"/></menu2>
        </menu1>
      </menubar>
      <label class="header" height="6vh" id="header" text="vcutils Demo Application" hjust="center"></label>
      <rows height="50vh">
        <columns>
          <rows>
            <label height="6vh" outline="true" id="info_label" text="Enter Command:" hjust="left"></label>
            <textbox text="Initial Command" id="cmd_input" onclick=""></textbox>
          </rows>
          <rows>
            <label height="6vh" outline="true" id="textarea_label" text="Multiline Input:" hjust="left"></label>
            <textarea text="This is a multiline text area. It supports word wrap, copy and paste, and cursor movement." id="multi_input" onclick=""></textarea>
          </rows>
        </columns>
      </rows>
      <rows>
        <button height="7vh" onclick="submitInput(event)" text="Submit"></button>
      </rows>
      <rows>
        <image id="demo_image" margin="1vh" fitheight="true" fitwidth="true" onclick="showImageDetails()"></image>
      </rows>
    </rows>
  </page>
  <page id="open">
    <button text="OK"/ onclick="universe.poppage();print('OK')">
    <button text="CANCEL"/ onclick="universe.poppage();print('CANCEL')">
  </page>
</root>"""

demo_css = """* { 
  backgroundcolor: #F8F8F8; 
  fontcolor: #333333; 
  outlinecolor: #DDDDDD; 
}

page { 
  backgroundcolor: #F0F0F0; 
}

rows, columns { 
  backgroundcolor: transparent; 
}

menubar { 
  backgroundcolor: #2C3E50; 
  fontcolor: #ECF0F1;  
  outlinecolor: #34495E;   
}

menu1 { 
  backgroundcolor: #34495E; 
  fontcolor: #ECF0F1; 
  outlinecolor: #2C3E50; 
  padding: 1vh; 
}

menu2 { 
  backgroundcolor: #34495E; 
  fontcolor: #ECF0F1; 
  outlinecolor: #2C3E50; 
  padding: 1vh; 
}

label { 
  backgroundcolor: #ECF0F1;  
  fontcolor: #2C3E50;           
  outlinecolor: #C8C8C8;      
  padding: 1vh; 
}

textbox, textarea { 
  backgroundcolor: #FFFFFF; 
  fontcolor: #2C3E50; 
  outlinecolor: #969696; 
  borderthickness: 1; 
  padding: 0.5vh; 
}

button { 
  backgroundcolor: #DB9834;   
  fontcolor: #FFFFFF; 
  outlinecolor: #B98029;      
  borderthickness: 2; 
  padding: 1vh; 
}

image { 
  bordercolor: #7F8C8D; 
  borderthickness: 2; 
}
"""

# ----------------------
# Main Demo
# ----------------------

try:
    fromjupyter
except:
    fromjupyter=0

if __name__ == "__main__" and not fromjupyter:
    from C__flaskdisplay import C__flaskdisplay
    display = C__flaskdisplay('demo')
    # Combine XML and CSS using apply_css
    combined_xml = apply_css(demo_xml, demo_css, False)
    open('/tmp/1.xml','w').write(combined_xml)
    props = {
        "width": 800,
        "height": 600,
        "startpage": "demo",
        "pagesxml": demo_xml,
        "css": "",
        "css_hard": demo_css
    }
    universe = C__UI_universe(display, **props)
    def customupdate(universe):
        def submitInput(event):
            print('submitInput')
            print(event.__dict__)
        universe.local_env=locals()
    universe.customupdate=customupdate
    universe.run()
