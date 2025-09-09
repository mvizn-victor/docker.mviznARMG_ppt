for F in {dockermviznarmg_ppt-flaskdisplay_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_detectron_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_2025-09-05,\
dockermviznarmg_ppt-mvizn_pptarmg_ui_2025-09-05};do
  date
  mkdir -p /opt/mvizn-docker-images__dockermviznarmg_ppt
  echo docker save -o /opt/mvizn-docker-images__dockermviznarmg_ppt/${F}.tar ghcr.io/mvizn/mvizn-docker-images:$F
  docker save -o /opt/mvizn-docker-images__dockermviznarmg_ppt/${F}.tar ghcr.io/mvizn/mvizn-docker-images:$F
done
date
echo done