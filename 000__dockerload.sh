for F in {dockermviznarmg_ppt-flaskdisplay_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_detectron_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_ui_2025-09-05};do
  date
  echo docker load -i /opt/mvizn-docker-images__dockermviznarmg_ppt/${F}.tar
  docker load -i /opt/mvizn-docker-images__dockermviznarmg_ppt/${F}.tar
done
date
echo done