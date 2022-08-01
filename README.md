# compare_sha
Script that compares the latest image sha with staging tag of AWS ECR and Harbor. In case the sha is different, script is activating Harbor replica in order to pull the new latest image from ECR.
