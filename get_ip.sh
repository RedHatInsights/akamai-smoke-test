echo $(dig $1 | egrep 'IN[[:space:]].*A[[:space:]].*[0-9][0-9]' | awk '{print $NF}')