"""Code-Based Evaluation UI page"""
import streamlit as st
import json
from core.services.evaluation_service import EvaluationService
from typing import Optional, List

def render_code_eval_page(evaluation_service: EvaluationService):
    """Render the Code-Based Evaluation page"""
    # Import helper functions
    from backend.services.data_service import save_judgment
    # TODO: evaluate_code_comprehensive is a complex wrapper - refactor to use EvaluationService directly
    from backend.services.evaluation_functions import evaluate_code_comprehensive  # type: ignore
    
    st.header("💻 Code-Based Evaluation")
    st.markdown("Evaluate code with syntax checking, execution testing, and quality metrics.")
    
    # Language options grouped by platform
    language_options = {
        "Backend Development": {
            "python": "Python",
            "javascript": "JavaScript (Node.js)",
            "typescript": "TypeScript",
            "java": "Java",
            "go": "Go"
        },
        "Web Development": {
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "html": "HTML",
            "css": "CSS"
        },
        "iOS Development": {
            "swift": "Swift",
            "objective-c": "Objective-C"
        },
        "Android Development": {
            "kotlin": "Kotlin",
            "java": "Java"
        }
    }
    
    # Flatten options for selectbox (use lang_code as unique key)
    language_dict = {}
    for category, langs in language_options.items():
        for lang_code, lang_name in langs.items():
            # If language already exists, keep the first occurrence (prefer backend context)
            if lang_code not in language_dict:
                language_dict[lang_code] = lang_name
    
    # Convert to sorted list for selectbox
    language_list = sorted(language_dict.items(), key=lambda x: x[1])
    
    language = st.selectbox(
        "Programming Language",
        options=[lang[0] for lang in language_list],
        format_func=lambda x: next((lang[1] for lang in language_list if lang[0] == x), x),
        help="Select the programming language. Execution testing requires appropriate runtime (e.g., node for JavaScript, swift for Swift). Some languages (TypeScript, Java, Kotlin) require compilation and may have limited execution support."
    )
    
    code = st.text_area(
        "Code to Evaluate:",
        height=300,
        placeholder="""def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

result = calculate_sum(5, 3)
print(result)""",
        key="code_input"
    )
    
    col_test1, col_test2 = st.columns(2)
    with col_test1:
        use_test_inputs = st.checkbox("Use Test Inputs", help="Provide test inputs for code execution")
        test_inputs = None
        if use_test_inputs:
            test_inputs_text = st.text_area(
                "Test Inputs (one per line):",
                height=100,
                placeholder="5\n3",
                key="test_inputs"
            )
            if test_inputs_text:
                test_inputs = [line.strip() for line in test_inputs_text.split('\n') if line.strip()]
    
    with col_test2:
        use_expected_output = st.checkbox("Check Expected Output", help="Verify if output matches expected result")
        expected_output = None
        if use_expected_output:
            expected_output = st.text_area(
                "Expected Output:",
                height=100,
                placeholder="8",
                key="expected_output"
            )
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        evaluate_code_btn = st.button("💻 Evaluate Code", type="primary", use_container_width=True)
    with col_btn2:
        save_code_enabled = st.checkbox("💾 Save to DB", value=True, key="save_code")
    
    # Initialize session state
    if 'code_eval_result' not in st.session_state:
        st.session_state.code_eval_result = None
    
    if evaluate_code_btn:
        if not code or not code.strip():
            st.warning("Please enter code to evaluate.")
        else:
            # Run evaluation synchronously with status updates
            with st.status("💻 Running code evaluation...", expanded=True) as status:
                status.write("📝 Step 1/6: Checking syntax...")
                # Note: evaluate_code_comprehensive runs all steps internally
                # We show progress messages but the actual work happens in the function
                try:
                    result = evaluate_code_comprehensive(
                        code, 
                        language, 
                        test_inputs=test_inputs,
                        expected_output=expected_output
                    )
                    status.write("✅ Step 2/6: Testing execution...")
                    status.write("✅ Step 3/6: Analyzing code quality...")
                    status.write("🔒 Step 4/6: Scanning for security vulnerabilities...")
                    status.write("👃 Step 5/6: Detecting code smells...")
                    status.write("📊 Step 6/6: Calculating advanced metrics...")
                    status.update(label="✅ Code evaluation complete", state="complete")
                    st.session_state.code_eval_result = result
                except Exception as e:
                    status.update(label="❌ Code evaluation failed", state="error")
                    st.session_state.code_eval_result = {"success": False, "error": str(e)}
                    st.error(f"❌ Error: {str(e)}")
    
    if st.session_state.code_eval_result is not None:
        result = st.session_state.code_eval_result
        
        if result.get("success"):
            st.success("✅ Code Evaluation Complete!")
            
            eval_results = result.get("results", {})
            
            # Display overall score
            overall = eval_results.get("overall_score", 0)
            execution_time = result.get("execution_time", 0)
            
            col_score, col_time = st.columns([2, 1])
            with col_score:
                st.markdown(f"### 🎯 Overall Score: **{overall:.2f}/10**")
            with col_time:
                st.markdown(f"### ⏱️ Execution Time: **{execution_time:.2f}s**")
            
            # Syntax Results
            st.markdown("### 📝 Syntax Check")
            syntax = eval_results.get("syntax", {})
            if syntax.get("valid"):
                st.success(f"✅ Valid syntax - {syntax.get('ast_nodes', 0)} AST nodes, Complexity: {syntax.get('complexity', 0)}")
                if syntax.get("warnings"):
                    st.warning("⚠️ Warnings:")
                    for warning in syntax["warnings"]:
                        st.write(f"- {warning}")
            else:
                st.error("❌ Syntax errors found:")
                for error in syntax.get("errors", []):
                    if isinstance(error, dict):
                        st.write(f"- Line {error.get('line', '?')}: {error.get('message', 'Unknown error')}")
                    else:
                        st.write(f"- {error}")
            
            # Execution Results
            st.markdown("### 🚀 Execution Test")
            execution = eval_results.get("execution", {})
            if execution.get("skipped"):
                st.info("⏭️ Execution skipped due to syntax errors")
            elif execution.get("success"):
                st.success(f"✅ Code executed successfully in {execution.get('execution_time', 0):.3f}s")
                if execution.get("output"):
                    st.code(execution["output"], language="text")
                if execution.get("output_match") is not None:
                    if execution["output_match"]:
                        st.success("✅ Output matches expected result")
                    else:
                        st.warning(f"⚠️ Output doesn't match expected. Expected: {execution.get('expected', 'N/A')}")
            else:
                st.error("❌ Execution failed:")
                if execution.get("error"):
                    st.code(execution["error"], language="text")
            
            # Quality Metrics
            st.markdown("### 📊 Code Quality Metrics")
            quality = eval_results.get("quality", {})
            col_q1, col_q2, col_q3, col_q4 = st.columns(4)
            
            with col_q1:
                st.metric("Lines of Code", quality.get("lines_of_code", 0))
            with col_q2:
                st.metric("Functions", quality.get("functions", 0))
            with col_q3:
                st.metric("Maintainability", f"{quality.get('maintainability', 0):.1f}/10")
            with col_q4:
                st.metric("Readability", f"{quality.get('readability', 0):.1f}/10")
            
            # Advanced Metrics (SonarQube-like)
            advanced_metrics = eval_results.get("advanced_metrics", {})
            if advanced_metrics:
                col_adv1, col_adv2, col_adv3 = st.columns(3)
                with col_adv1:
                    st.metric("Cyclomatic Complexity", advanced_metrics.get("cyclomatic_complexity", 0))
                with col_adv2:
                    st.metric("Cognitive Complexity", advanced_metrics.get("cognitive_complexity", 0))
                with col_adv3:
                    tech_debt = advanced_metrics.get("technical_debt_ratio", 0)
                    st.metric("Technical Debt Ratio", f"{tech_debt:.1f}%")
            
            if quality.get("issues"):
                st.warning("⚠️ Quality Issues:")
                for issue in quality["issues"]:
                    st.write(f"- {issue}")
            
            # Security Vulnerabilities (SonarQube-like)
            security = eval_results.get("security", {})
            if security and security.get("vulnerability_count", 0) > 0:
                st.markdown("### 🔒 Security Vulnerabilities")
                vuln_count = security.get("vulnerability_count", 0)
                blocker_count = security.get("blocker_count", 0)
                critical_count = security.get("critical_count", 0)
                major_count = security.get("major_count", 0)
                
                col_sec1, col_sec2, col_sec3, col_sec4 = st.columns(4)
                with col_sec1:
                    st.metric("Total", vuln_count)
                with col_sec2:
                    st.metric("🔴 Blocker", blocker_count)
                with col_sec3:
                    st.metric("🟠 Critical", critical_count)
                with col_sec4:
                    st.metric("🟡 Major", major_count)
                
                vulnerabilities = security.get("vulnerabilities", [])
                if vulnerabilities:
                    # Group by severity
                    for severity in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
                        severity_vulns = [v for v in vulnerabilities if v.get("severity") == severity]
                        if severity_vulns:
                            severity_color = {
                                "BLOCKER": "🔴",
                                "CRITICAL": "🟠",
                                "MAJOR": "🟡",
                                "MINOR": "🟢",
                                "INFO": "🔵"
                            }
                            with st.expander(f"{severity_color.get(severity, '⚪')} {severity} ({len(severity_vulns)})", expanded=(severity in ["BLOCKER", "CRITICAL"])):
                                for vuln in severity_vulns:
                                    line = vuln.get("line", "?")
                                    message = vuln.get("message", "Unknown issue")
                                    st.write(f"**Line {line}:** {message}")
            
            # Code Smells (SonarQube-like)
            code_smells = eval_results.get("code_smells", {})
            if code_smells and code_smells.get("smell_count", 0) > 0:
                st.markdown("### 👃 Code Smells")
                smell_count = code_smells.get("smell_count", 0)
                major_count = code_smells.get("major_count", 0)
                minor_count = code_smells.get("minor_count", 0)
                info_count = code_smells.get("info_count", 0)
                
                col_smell1, col_smell2, col_smell3, col_smell4 = st.columns(4)
                with col_smell1:
                    st.metric("Total", smell_count)
                with col_smell2:
                    st.metric("🟡 Major", major_count)
                with col_smell3:
                    st.metric("🟢 Minor", minor_count)
                with col_smell4:
                    st.metric("🔵 Info", info_count)
                
                smells = code_smells.get("smells", [])
                if smells:
                    # Group by severity
                    for severity in ["MAJOR", "MINOR", "INFO"]:
                        severity_smells = [s for s in smells if s.get("severity") == severity]
                        if severity_smells:
                            severity_color = {
                                "MAJOR": "🟡",
                                "MINOR": "🟢",
                                "INFO": "🔵"
                            }
                            with st.expander(f"{severity_color.get(severity, '⚪')} {severity} ({len(severity_smells)})", expanded=(severity == "MAJOR")):
                                for smell in severity_smells:
                                    line = smell.get("line", "?")
                                    message = smell.get("message", "Unknown issue")
                                    rule = smell.get("rule", "unknown")
                                    st.write(f"**Line {line}** ({rule}): {message}")
            
            # Trace information
            with st.expander("🔍 Evaluation Trace", expanded=False):
                st.json(eval_results.get("trace", {}))
            
            # Save to database
            if save_code_enabled:
                try:
                    judgment_text = f"Code Evaluation - Overall Score: {overall:.2f}/10 | Syntax: {'Valid' if syntax.get('valid') else 'Invalid'} | Execution: {'Success' if execution.get('success') else 'Failed'}"
                    judgment_id = save_judgment(
                        question=f"Code Evaluation ({language})",
                        response_a=code[:500] + "..." if len(code) > 500 else code,
                        response_b="",
                        model_a="Code-Based Evaluation",
                        model_b="",
                        judge_model="Code Analyzer",
                        judgment=judgment_text,
                        judgment_type="code_evaluation",
                        evaluation_id=eval_results.get("evaluation_id"),
                        metrics_json=json.dumps(eval_results),
                        trace_json=json.dumps(eval_results.get("trace", {}))
                    )
                    st.success(f"💾 Saved to database (ID: {judgment_id})")
                except Exception as e:
                    st.warning(f"⚠️ Could not save to database: {str(e)}")
            
            if st.button("🔄 New Evaluation", key="new_code_eval"):
                st.session_state.code_eval_result = None
                st.session_state.code_eval_running = False
                st.rerun()
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            if st.button("🔄 Retry", key="retry_code_eval"):
                st.session_state.code_eval_result = None
                st.session_state.code_eval_running = False
                st.rerun()

