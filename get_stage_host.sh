echo $(dig cloud.redhat.com | egrep '.*\.akamaiedge.net.[[:space:]][0-9]*' | awk '{print $1}' | sed 's/akamaiedge/akamaiedge-staging/'  | sed 's/.$//')
