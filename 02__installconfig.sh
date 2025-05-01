#02__installconfig.sh
if [ ! -e ~/PPTARMG_config ]; then
	echo "PPTARMG_config not exists: copying sample config"
	rsync -av PPTARMG_config.sample/ ~/PPTARMG_config/
else
	echo "PPTARMG_config already exists: not copying sample config"
fi