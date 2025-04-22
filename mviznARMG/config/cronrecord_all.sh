#!/bin/bash

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
camip=10.140.48.140
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnlsbc
camip=10.140.48.141
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl4xb
camip=10.140.48.142
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl20b
camip=10.140.48.143
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl20f
camip=10.140.48.144
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=tl4xf
camip=10.140.48.145
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbb
camip=10.140.48.148
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbc
camip=10.140.48.149
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts4xf
camip=10.140.48.150
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts20f
camip=10.140.48.151
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts20b
camip=10.140.48.152
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ts4xb
camip=10.140.48.153
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


params="?videocodec=h264&videomaxbitrate=512&fps=10&resolution=1280x720"



cam=cnlsbf
camip=10.140.48.139
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=cnssbf
camip=10.140.48.147
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


params="?videocodec=h264&videomaxbitrate=512&fps=2&resolution=1280x720"



cam=ovtrls
camip=10.140.48.131
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovtrss
camip=10.140.48.132
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovls
camip=10.140.48.133
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=ovss
camip=10.140.48.134
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=pmnls
camip=10.140.48.146
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &


cam=pmnss
camip=10.140.48.154
ffmpeg ${ffinoptions} "rtsp://root:pass@$camip${path}${params}" ${ffoutoptions} ${outvidpath}$cam-${filename} </dev/null >/dev/null 2>${outlogpath}$cam.log &

