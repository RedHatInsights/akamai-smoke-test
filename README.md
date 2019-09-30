# Akamai Smoke Test

## Prerequesites

* python 3
* `sh prep.sh` to install dependencies

## Running

`Staging` and `production` refer to the status of the property in Akamai

### All

`sh run_all.sh` to run smoke tests against all environments

### Staging

`sh run_stage.sh` to run against all stage environments
`sh run_stage_stable.sh` to run against stage *stable*
`sh run_stage_beta.sh` to run against stage *beta*

### Production

`sh run_prod.sh` to run against all prod environments
`sh run_prod_stable.sh` to run against prod *stable*
`sh run_prod_beta.sh` to run against prod *beta*
