#!/bin/bash
killall ffmpeg
basedir="/opt/captures/"
logdir="logs/"
videodir="vids/"

subdirname="`date +%Y-%m-%d`/"
filename="`date +%H_%M`.mp4"

mkdir -p ${basedir}${videodir}${subdirname}
mkdir -p ${basedir}${logdir}${subdirname}
outvidpath=${basedir}${videodir}${subdirname}
outlogpath=${basedir}${logdir}${subdirname}

path="/axis-media/media.amp"
params="?videocodec=h264&videomaxbitrate=512&fps=4&resolution=1280x720"
recordtimechunk="300"

ffinoptions="-rtsp_transport tcp -i"
ffoutoptions="-vcodec copy -an -t "$recordtimechunk
redirecter="</dev/null >/dev/null 2>"



cam=cnlsbb
camip=10.140.98.12
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnlsbc
camip=10.140.98.13
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl4xb
camip=10.140.98.14
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl20b
camip=10.140.98.15
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl20f
camip=10.140.98.16
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl4xf
camip=10.140.98.17
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbb
camip=10.140.98.20
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbc
camip=10.140.98.21
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts4xf
camip=10.140.98.22
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts20f
camip=10.140.98.23
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts20b
camip=10.140.98.24
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts4xb
camip=10.140.98.25
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


params="?videocodec=h264&videomaxbitrate=512&fps=10&resolution=1280x720"



cam=cnlsbf
camip=10.140.98.11
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbf
camip=10.140.98.19
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


params="?videocodec=h264&videomaxbitrate=512&fps=2&resolution=1280x720"



cam=ovtrls
camip=10.140.98.3
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovtrss
camip=10.140.98.4
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovls
camip=10.140.98.5
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovss
camip=10.140.98.6
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=pmnls
camip=10.140.98.18
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=pmnss
camip=10.140.98.26
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &

