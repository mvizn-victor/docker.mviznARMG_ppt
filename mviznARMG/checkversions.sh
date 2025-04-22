cat pyfiles.txt shfiles.txt txtfiles.txt|xargs grep '#version:' > version_all.txt
cat weightfiles.txt|xargs md5sum >> version_all.txt
