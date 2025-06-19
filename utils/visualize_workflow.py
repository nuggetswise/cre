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

def create_text_based_diagram(workflow_text):
    """Create a simple text-based workflow diagram when Graphviz is not available"""
    if isinstance(workflow_text, dict):
        workflow_text = "\n".join([f"{key}: {value}" for key, value in workflow_text.items()])
    
    # Extract step lines and filter empty lines
    steps = [line.strip() for line in workflow_text.split("\n") if line.strip()]
    
    # Process steps to identify numbered steps (1., 2., etc.)
    processed_steps = []
    current_step = ""
    
    for step in steps:
        # Check if line starts with a number followed by period
        if step and step[0].isdigit() and ". " in step[:5]:
            if current_step:  # Save previous step if exists
                processed_steps.append(current_step)
            current_step = step
        elif current_step:  # Continuation of current step
            current_step += " " + step
        else:  # Just in case there's content before the first numbered step
            processed_steps.append(step)
    
    # Add the last step if it exists
    if current_step:
        processed_steps.append(current_step)
    
    # If no numbered steps were found, use the original lines
    if not processed_steps:
        processed_steps = steps
    
    # Assign steps to systems
    tools = ["Salesforce", "DocuSign", "Google Drive", "Slack", "Email"]
    system_steps = {tool: [] for tool in tools}
    
    for i, step in enumerate(processed_steps):
        assigned = False
        for tool in tools:
            if tool.lower() in step.lower():
                system_steps[tool].append((i+1, step))
                assigned = True
                break
        
        if not assigned:
            # Assign to a system based on step number
            system_steps[tools[i % len(tools)]].append((i+1, step))
    
    # Create HTML for the diagram
    html = """
    <style>
    .workflow-container {
        display: flex;
        flex-direction: column;
        width: 100%;
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
    }
    .system-row {
        display: flex;
        border-bottom: 1px solid #ddd;
    }
    .system-row:last-child {
        border-bottom: none;
    }
    .system-name {
        width: 150px;
        padding: 10px;
        background-color: #f0f8ff;
        font-weight: bold;
        border-right: 1px solid #ddd;
    }
    .system-steps {
        flex: 1;
        padding: 10px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
    }
    .step-box {
        background-color: #ffffcc;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 8px;
        margin: 5px;
        max-width: 250px;
        font-size: 12px;
    }
    .step-box span {
        font-weight: bold;
    }
    .arrow {
        color: #999;
        margin: 0 5px;
        font-size: 16px;
    }
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
            # Extract step title
            match = re.search(r"(\d+\.\s*)(.*?):", step) if ":" in step else re.search(r"(\d+\.\s*)(.*)", step)
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
    return html

def render_workflow(workflow_text):
    # Create expander for the workflow text
    with st.expander("View detailed workflow text"):
        st.code(workflow_text)
    
    st.write("##### Swimlane Workflow Diagram")
    
    try:
        # Try using Graphviz if available
        if GRAPHVIZ_AVAILABLE and os.system("which dot") == 0:  # Check if dot command exists
            # Create the graph with horizontal swimlane format
            dot = graphviz.Digraph()
            dot.attr(rankdir="LR", size="16,8", dpi="100", ranksep="0.5", nodesep="0.5")
            
            # Extract step lines and filter empty lines
            steps = [line.strip() for line in workflow_text.split("\n") if line.strip()]
            
            # Process steps to identify numbered steps (1., 2., etc.)
            processed_steps = []
            current_step = ""
            
            for step in steps:
                # Check if line starts with a number followed by period
                if step and step[0].isdigit() and ". " in step[:5]:
                    if current_step:  # Save previous step if exists
                        processed_steps.append(current_step)
                    current_step = step
                elif current_step:  # Continuation of current step
                    current_step += " " + step
                else:  # Just in case there's content before the first numbered step
                    processed_steps.append(step)
            
            # Add the last step if it exists
            if current_step:
                processed_steps.append(current_step)
            
            # If no numbered steps were found, use the original lines
            if not processed_steps:
                processed_steps = steps
            
            # Create swimlanes as subgraphs
            tools = ["Salesforce", "DocuSign", "Google Drive", "Slack", "Email"]
            tool_subgraphs = {}
            
            for i, tool in enumerate(tools):
                sg = graphviz.Digraph(name=f"cluster_{tool}")
                sg.attr(label=tool, style="filled", fillcolor=f"lightblue{(i % 2) + 1}", 
                        fontsize="14", fontcolor="black", penwidth="2", fontname="Arial")
                tool_subgraphs[tool.lower()] = sg
            
            # Process each step and assign to appropriate swimlane
            node_placements = {}  # To track which nodes are in which swimlane
            nodes = []
            
            for i, step in enumerate(processed_steps):
                # Extract step title and short description
                match = re.search(r"(\d+\.\s*)(.*?):", step) if ":" in step else re.search(r"(\d+\.\s*)(.*)", step)
                if match:
                    step_number = match.group(1).strip()
                    step_title = match.group(2).strip()
                else:
                    step_number = f"{i+1}."
                    step_title = step[:30] + "..." if len(step) > 30 else step
                    
                # Clean and trim step title if too long
                if len(step_title) > 25:
                    step_title = step_title[:22] + "..."
                    
                # Assign to swimlane based on content
                assigned_tool = None
                for tool in tools:
                    if tool.lower() in step.lower():
                        assigned_tool = tool.lower()
                        break
                        
                # If no tool match found, assign to default
                if assigned_tool is None:
                    assigned_tool = tools[i % len(tools)].lower()
                    
                # Create the node with step number and title
                node_id = f"step_{i}"
                label = f"{step_number} {step_title}"
                
                nodes.append((node_id, assigned_tool, i, label))
                node_placements[node_id] = assigned_tool
            
            # Add nodes to swimlanes with invisible nodes for better alignment
            for swimlane in tool_subgraphs:
                swimlane_nodes = [n for n in nodes if n[1] == swimlane]
                
                # Add phantom nodes if this swimlane has no actual nodes
                if not swimlane_nodes:
                    phantom_id = f"phantom_{swimlane}"
                    tool_subgraphs[swimlane].node(phantom_id, label="", shape="none", width="0", height="0", style="invis")
                
                # Add actual nodes
                for node_id, _, step_num, label in swimlane_nodes:
                    # Add node to appropriate swimlane with nice styling
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
            
            # Add all swimlanes to the main graph
            for sg in tool_subgraphs.values():
                dot.subgraph(sg)
            
            # Connect steps in order, with nice edge styling
            for i in range(len(nodes) - 1):
                current_node = nodes[i][0]
                next_node = nodes[i + 1][0]
                
                # Style edges differently if crossing swimlanes
                if node_placements[current_node] != node_placements[next_node]:
                    dot.edge(current_node, next_node, color="blue", penwidth="1.5", style="dashed")
                else:
                    dot.edge(current_node, next_node, color="black", penwidth="1.5")
            
            # Use a container to control the height
            container = st.container()
            with container:
                # Display with HTML to control height
                svg_data = dot.pipe(format="svg").decode("utf-8")
                st.components.v1.html(
                    f'<div style="height: 600px; width: 100%; overflow: auto; background-color: white;">{svg_data}</div>',
                    height=650,
                    scrolling=True
                )
        else:
            # Use the fallback HTML-based visualization
            html_diagram = create_text_based_diagram(workflow_text)
            st.components.v1.html(html_diagram, height=500, scrolling=True)
            st.info("Note: For a more detailed visualization, install Graphviz system binaries: `brew install graphviz` (macOS) or `apt-get install graphviz` (Linux)")
    except Exception as e:
        # If anything fails, use the fallback visualization
        st.error(f"Error creating diagram: {str(e)}")
        html_diagram = create_text_based_diagram(workflow_text)
        st.components.v1.html(html_diagram, height=500, scrolling=True)
        st.info("For a more detailed visualization, install Graphviz: `brew install graphviz` (macOS) or `apt-get install graphviz` (Linux)")
