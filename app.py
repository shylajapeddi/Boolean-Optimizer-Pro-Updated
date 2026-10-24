    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, "circuits.v")
        testbench_path = os.path.join(temp_dir, "testbench.v")
        output_path = os.path.join(temp_dir, "simulation.out")

        with open(source_path, "w", encoding="utf-8") as source_file:
            source_file.write(verilog)
        with open(testbench_path, "w", encoding="utf-8") as testbench_file:
            testbench_file.write(testbench)

        compile_result = subprocess.run(
            ["iverilog", "-o", output_path, source_path, testbench_path],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if compile_result.returncode:
            return "Compilation failed:\n" + compile_result.stderr

        run_result = subprocess.run(
            ["vvp", output_path], capture_output=True, text=True, timeout=20
        )
        return (run_result.stdout or "") + (run_result.stderr or "")


def run_optimizer(expression):
    try:
        normalized, original, variables = parse_boolean_expression(expression)
        simplified = sp.simplify_logic(original, form="dnf", force=True)
        table = make_truth_table(original, simplified, variables)
        equivalence = "PASS" if (table["Original F"] == table["Optimized F"]).all() else "FAIL"
        verilog = make_verilog(original, simplified, variables)
        testbench = make_testbench(variables)
        simulation = simulate_verilog(verilog, testbench)
        kmap = kmap_html(table, variables, simplified)
        circuits = make_circuits(original, simplified)
        waveform = make_waveform(table, variables)
        status = (
            f"**Boolean equivalence: {equivalence}**\n\n"
            f"Variables detected: {', '.join(variables) if variables else 'none'} · "
            f"Truth-table rows: {len(table)}"
        )
        return (
            normalized, str(simplified), status, table, kmap, circuits,
            waveform, verilog, testbench, simulation,
        )
    except Exception as exc:
        message = f"Could not process expression: {exc}"
        return (
            "", "", message, pd.DataFrame(),
            "<div class='note'>K-map unavailable until a valid expression is entered.</div>",
            "<div class='note'>Circuit diagram unavailable until a valid expression is entered.</div>",
            None, "", "", "",
        )


CSS = """
.gradio-container {max-width: 1250px !important}
.kmap-wrap, .circuit-card {padding:16px;border:1px solid var(--border-color-primary);border-radius:14px;margin:8px 0;background:var(--background-fill-secondary)}
.kmap {border-collapse:separate;border-spacing:5px;margin:10px auto}
.kmap th {padding:9px 12px;text-align:center;background:var(--background-fill-primary);border-radius:8px}
.kmap td {min-width:48px;height:42px;text-align:center;font-size:18px;font-weight:700;border-radius:8px}
.kmap td.one {background:#d9f2df;color:#176534;border:2px solid #21864b}
.kmap td.zero {background:var(--background-fill-primary);color:var(--body-text-color);border:1px solid var(--border-color-primary)}
.note {color:var(--body-text-color);opacity:.8;font-size:14px}
.circuits {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.circuit-card h3 {margin-top:0;text-align:center}
.circuit-card svg {width:100%;height:auto;max-height:500px}
@media(max-width:760px){.circuits{grid-template-columns:1fr}}
"""

with gr.Blocks(title=APP_TITLE, css=CSS, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        f"# 🔌 {APP_TITLE}\n"
        "Simplify Boolean logic, inspect the truth table and K-map, compare circuit diagrams, "
        "view output waveforms, generate Verilog/testbench, and simulate when Icarus Verilog is available."
    )
    with gr.Row():
        expression = gr.Textbox(
            label="Boolean expression",
            value="(A & B) | (A & ~B)",
            placeholder="Example: (A & B) | (A & ~B)",
            scale=5,
        )
        optimize_btn = gr.Button("Optimize and Verify", variant="primary", scale=1)

    gr.Markdown(
        "**Operators:** `&` AND · `|` OR · `~` NOT · parentheses for grouping. **Variables:** A–F."
    )
    with gr.Row():
        original_out = gr.Textbox(label="Original expression", interactive=False)
        optimized_out = gr.Textbox(label="Optimized expression", interactive=False)
    status_out = gr.Markdown()

    with gr.Tab("Truth Table"):
        truth_table = gr.Dataframe(label="Truth table", interactive=False, wrap=True)
    with gr.Tab("K-map"):
        kmap_out = gr.HTML()
    with gr.Tab("Circuit Diagrams"):
        circuit_out = gr.HTML()
    with gr.Tab("Digital Waveform"):
        waveform_out = gr.Plot(label="Output waveform")
        gr.Markdown(
            "Note: this waveform compares truth-table output values by input combination. "
            "It is not a timed VCD waveform."
        )
    with gr.Tab("Generated Verilog"):
        verilog_out = gr.Code(label="Generated Verilog", language="python", interactive=False)
    with gr.Tab("Generated Testbench"):
        testbench_out = gr.Code(label="Generated testbench", language="python", interactive=False)
    with gr.Tab("Icarus Verilog Simulation"):
        simulation_out = gr.Textbox(label="Simulation output", lines=14, interactive=False)

    output_components = [
        original_out, optimized_out, status_out, truth_table, kmap_out,
        circuit_out, waveform_out, verilog_out, testbench_out, simulation_out,
    ]
    optimize_btn.click(run_optimizer, inputs=[expression], outputs=output_components)
    demo.load(run_optimizer, inputs=[expression], outputs=output_components)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        share=False,
    )
