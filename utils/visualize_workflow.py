import streamlit as st
import re
import os
import base64
from io import BytesIO
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

def extract_intro_and_steps(workflow_text):
    """
    Extract the intro/summary sentence and actual numbered steps from the workflow text.
    Returns (intro_sentence, steps_list)
    """
    lines = [line.strip() for line in workflow_text.split("\n") if line.strip()]
    steps = []
    intro = None
    for line in lines:
        # Only consider lines that start with a step number (e.g., '1. ', '2. ')
        if re.match(r"^\d+\. ", line):
            steps.append(line)
        elif intro is None:
            # The first non-step line is considered the intro/summary
            intro = line
    return intro, steps

def create_text_based_diagram(workflow_text):
    intro, steps = extract_intro_and_steps(workflow_text)
    # Assign steps to systems
    tools = ["Salesforce", "DocuSign", "Google Drive", "Slack", "Email"]
    system_steps = {tool: [] for tool in tools}
    for i, step in enumerate(steps):
        assigned = False
        for tool in tools:
            if tool.lower() in step.lower():
                system_steps[tool].append((i+1, step))
                assigned = True
                break
        if not assigned:
            system_steps[tools[i % len(tools)]].append((i+1, step))
    # Create HTML for the diagram
    html = """
    <style>
    .workflow-container { display: flex; flex-direction: column; width: 100%; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }
    .system-row { display: flex; border-bottom: 1px solid #ddd; }
    .system-row:last-child { border-bottom: none; }
    .system-name { width: 150px; padding: 10px; background-color: #f0f8ff; font-weight: bold; border-right: 1px solid #ddd; }
    .system-steps { flex: 1; padding: 10px; display: flex; flex-wrap: wrap; align-items: center; }
    .step-box { background-color: #ffffcc; border: 1px solid #ddd; border-radius: 4px; padding: 8px; margin: 5px; max-width: 250px; font-size: 12px; }
    .step-box span { font-weight: bold; }
    .arrow { color: #999; margin: 0 5px; font-size: 16px; }
    </style>
    <div class="workflow-container">
    """
    for tool in tools:
        tool_steps = system_steps[tool]
        if not tool_steps:
            continue
        html += f'<div class="system-row">'
        html += f'<div class="system-name">{tool}</div>'
        html += f'<div class="system-steps">'
        for i, (step_num, step) in enumerate(tool_steps):
            match = re.search(r"(\d+\.\s*)(.*)", step)
            if match:
                step_number = match.group(1).strip()
                step_title = match.group(2).strip()
            else:
                step_number = f"{step_num}."
                step_title = step[:50] + "..." if len(step) > 50 else step
            html += f'<div class="step-box"><span>{step_number}</span> {step_title}</div>'
            if i < len(tool_steps) - 1:
                html += '<div class="arrow">→</div>'
        html += '</div></div>'
    html += '</div>'
    return intro, html

def render_workflow(workflow_text):
    intro, steps = extract_intro_and_steps(workflow_text)
    # Show the intro/summary sentence above the diagram if it exists
    if intro:
        st.info(intro)
    with st.expander("View detailed workflow text"):
        st.code(workflow_text)
    st.write("##### Swimlane Workflow Diagram")
    try:
        if GRAPHVIZ_AVAILABLE and os.system("which dot") == 0:
            dot = graphviz.Digraph()
            dot.attr(rankdir="LR", size="16,8", dpi="100", ranksep="0.5", nodesep="0.5")
            tools = ["Salesforce", "DocuSign", "Google Drive", "Slack", "Email"]
            tool_subgraphs = {}
            for i, tool in enumerate(tools):
                sg = graphviz.Digraph(name=f"cluster_{tool}")
                sg.attr(label=tool, style="filled", fillcolor=f"lightblue{(i % 2) + 1}", fontsize="14", fontcolor="black", penwidth="2", fontname="Arial")
                tool_subgraphs[tool.lower()] = sg
            node_placements = {}
            nodes = []
            for i, step in enumerate(steps):
                match = re.search(r"(\d+\.\s*)(.*)", step)
                if match:
                    step_number = match.group(1).strip()
                    step_title = match.group(2).strip()
                else:
                    step_number = f"{i+1}."
                    step_title = step[:30] + "..." if len(step) > 30 else step
                if len(step_title) > 25:
                    step_title = step_title[:22] + "..."
                assigned_tool = None
                for tool in tools:
                    if tool.lower() in step.lower():
                        assigned_tool = tool.lower()
                        break
                if assigned_tool is None:
                    assigned_tool = tools[i % len(tools)].lower()
                node_id = f"step_{i}"
                label = f"{step_number} {step_title}"
                nodes.append((node_id, assigned_tool, i, label))
                node_placements[node_id] = assigned_tool
            for swimlane in tool_subgraphs:
                swimlane_nodes = [n for n in nodes if n[1] == swimlane]
                if not swimlane_nodes:
                    phantom_id = f"phantom_{swimlane}"
                    tool_subgraphs[swimlane].node(phantom_id, label="", shape="none", width="0", height="0", style="invis")
                for node_id, _, step_num, label in swimlane_nodes:
                    tool_subgraphs[swimlane].node(
                        node_id, 
                        label=label, 
                        shape="box", 
                        style="filled", 
                        fillcolor="#ffffcc", 
                        fontsize="12",
                        fontname="Arial",
                        margin="0.15",
                        color="black",
                        penwidth="1.5"
                    )
            for sg in tool_subgraphs.values():
                dot.subgraph(sg)
            for i in range(len(nodes) - 1):
                current_node = nodes[i][0]
                next_node = nodes[i + 1][0]
                if node_placements[current_node] != node_placements[next_node]:
                    dot.edge(current_node, next_node, color="blue", penwidth="1.5", style="dashed")
                else:
                    dot.edge(current_node, next_node, color="black", penwidth="1.5")
            container = st.container()
            with container:
                svg_data = dot.pipe(format="svg").decode("utf-8")
                st.components.v1.html(
                    f'<div style="height: 600px; width: 100%; overflow: auto; background-color: white;">{svg_data}</div>',
                    height=650,
                    scrolling=True
                )
        else:
            intro, html_diagram = create_text_based_diagram(workflow_text)
            st.components.v1.html(html_diagram, height=500, scrolling=True)
            st.info("Note: For a more detailed visualization, install Graphviz system binaries: `brew install graphviz` (macOS) or `apt-get install graphviz` (Linux)")
    except Exception as e:
        st.error(f"Error creating diagram: {str(e)}")
        intro, html_diagram = create_text_based_diagram(workflow_text)
        st.components.v1.html(html_diagram, height=500, scrolling=True)
        st.info("For a more detailed visualization, install Graphviz: `brew install graphviz` (macOS) or `apt-get install graphviz` (Linux)")
