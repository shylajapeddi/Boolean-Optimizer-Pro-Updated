# Boolean Expression Optimizer & Circuit Simulator Pro

A Gradio web app for Boolean-expression simplification and digital-logic inspection.

## Features
- Boolean simplification and equivalence checking
- Truth-table generation
- K-map display for up to four variables
- Original and optimized expression-tree circuit diagrams
- Truth-table-based output waveform comparison
- Verilog and exhaustive testbench generation
- Icarus Verilog simulation when installed

## Operators
- `&` AND
- `|` OR
- `~` NOT
- Parentheses for grouping
- Variables A–F

## Run locally
Install Python 3.12+, then:
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:7860`.

## Deploy to Render
- Connect this repository as a Web Service.
- Leave **Root Directory** blank when the files are at repository root.
- Set **Dockerfile Path** to `./Dockerfile`.
- Deploy the latest commit.
- Open the public `https://...onrender.com` URL shown on the Render service page. Do not open `0.0.0.0`.

## Notes
The waveform shown is a truth-table sequence comparison, not a timed waveform from a VCD file. The circuit view is a generated expression-tree schematic; review the generated Verilog and simulation output for logic verification.
