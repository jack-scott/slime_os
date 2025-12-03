# Development Files

This directory contains files that are NOT uploaded to the Pico hardware:

- **Documentation** (*.md files): Design docs, implementation notes, testing guides
- **Simulator**: `run_simulator.py` and simulator device/driver files
- **Development scripts**: Testing scripts, compatibility shims
- **Dependencies**: `requirements.txt` for desktop Python dependencies

## Running the Simulator

From the parent directory:
```bash
python3 dev/run_simulator.py
```

## Deploying to Hardware

From the parent directory:
```bash
./deploy_to_pico.sh
```

This will upload only the necessary files (main.py, config.py, apps/, lib/, slime/) to the Pico.
