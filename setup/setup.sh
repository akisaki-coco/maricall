echo "Starting setup for Maricall on Termux..."
cd ~

echo "Updating package lists..."
pkg update -y
pkg upgrade -y

echo "Installing necessary packages..."
pkg install -y python3 python3-pip sox termux-api
echo "Installing Python dependencies..."
pip3 install --upgrade pip

echo "cloning the repository..."
git clone https://github.com/akisaki-coco/maricall.git maricall

echo "Setup complete!"
