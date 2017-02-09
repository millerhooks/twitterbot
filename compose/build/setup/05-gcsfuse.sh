./build/scripts/style_bash_message.sh " Setup Google Cloud Storage | Fuse"

export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list

export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# Update and install the Cloud SDK
apt-get update && apt-get install -y google-cloud-sdk gcsfuse

cp /build/deploy/etc/fstab /etc/fstab

