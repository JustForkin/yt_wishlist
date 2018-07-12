echo "Switching into virtual environment..."
source p3/bin/activate

echo "Starting server..."
nohup python src/main.py &>/tmp/server &

echo "Done."
