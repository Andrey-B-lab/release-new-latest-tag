Octopus Deploy pipeline that comparing sha of Harbor and ECR and creating release if needed.
Contains three steps.

# compare_sha
Script that compares the latest image sha with staging tag of AWS ECR and Harbor. In case the sha is different, script is activating Harbor replica in order to pull the new latest image from ECR.

# get-latest-ecr-tag
Script that stores the latest ECR tag as Octopus variable.

# create_octopus_release
Script that creating release in Octopus Deplo using the tag form the pevious step.
