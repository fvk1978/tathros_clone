# SETUP #

1. Define the Google Maps key (and optionally other env vars) in ENVIRONMENT file

2. Optionally change POSTGRES_USER, POSTGRES_PASSWORD and POSTGRES_DB in the services section of wercker.yml file

3. run `$ werker dev --publish 8000` to start container

4. Access http://localhost:8000

#### ALL DONE ####

# Development workflow#

- All features or anything which is not a one liner goes into a branch which results in a PR to master
 which must CRed required in order to merge.
- One liners and small patches can go to develop, with a PR to master.
- No commits, nor rebases on master

#### System requirements to have Postgresql + gis extension ####

postgis:
`$ sudo apt-get install postgis`

postgres:
`$ sudo apt-get install psql`