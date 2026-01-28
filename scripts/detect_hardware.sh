#!/bin/bash

# Default values
TOTAL_RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
HAS_NVIDIA=false
VRAM_GB=0
CPU_ARCH=$(uname -m)

echo "Scanning hardware..."
echo "CPU Architecture: $CPU_ARCH"
echo "Total RAM: ${TOTAL_RAM_GB}GB"

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    HAS_NVIDIA=true
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | awk '{s+=$1} END {print s}')
    VRAM_GB=$((VRAM_MB / 1024))
    echo "NVIDIA GPU detected with ${VRAM_GB}GB VRAM"
else
    echo "No NVIDIA GPU detected via nvidia-smi"
fi

# Tier Selection Logic
SELECTED_MODEL="llama3.2:1b"
TIER="Stage 1 (Low End)"

if [ "$HAS_NVIDIA" = true ]; then
    if [ "$VRAM_GB" -ge 32 ]; then
        SELECTED_MODEL="llama3.1:70b"
        TIER="Stage 5 (GPU 32GB+)"
    elif [ "$VRAM_GB" -ge 12 ]; then
        SELECTED_MODEL="llama3.1:8b" # Could be 70b-q2 but 8b-q8/f16 is better
        TIER="Stage 4 (GPU 12-32GB)"
    elif [ "$VRAM_GB" -ge 8 ]; then
        SELECTED_MODEL="llama3.1:8b"
        TIER="Stage 3 (GPU 8-12GB)"
    else
        # Small GPU, fallback to RAM check
        if [ "$TOTAL_RAM_GB" -ge 16 ]; then
            SELECTED_MODEL="llama3.2:3b"
            TIER="Stage 2 (CPU/Small GPU + 16GB RAM)"
        else
            SELECTED_MODEL="llama3.2:1b"
            TIER="Stage 1 (Low End)"
        fi
    fi
else
    if [ "$TOTAL_RAM_GB" -ge 16 ]; then
        SELECTED_MODEL="llama3.2:3b"
        TIER="Stage 2 (CPU + 16GB RAM)"
    else
        SELECTED_MODEL="llama3.2:1b"
        TIER="Stage 1 (Low End)"
    fi
fi

echo "Selected Tier: $TIER"
echo "Selected Model: $SELECTED_MODEL"

# Save to .env
cat << EOF > .env
SELECTED_MODEL=$SELECTED_MODEL
HARDWARE_TIER="$TIER"
EOF

echo ".env file generated successfully."
