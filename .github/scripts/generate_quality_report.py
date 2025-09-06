#!/usr/bin/env python3
"""
Generate unified quality report from cross-language static analysis results.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET


class QualityReportGenerator:
    """Generate comprehensive quality reports from analysis artifacts."""
    
    def __init__(self, artifacts_dir: str = "analysis-reports"):
        self.artifacts_dir = Path(artifacts_dir)
        self.report_data = {
            "python": {},
            "rust": {},
            "gdscript": {},
            "coverage": {},
            "security": {},
            "performance": {}
        }
    
    def collect_python_analysis(self):
        """Collect Python static analysis results."""
        
        # MyPy results
        mypy_dir = self.artifacts_dir / "python-mypy-analysis"
        if mypy_dir.exists():
            self.report_data["python"]["mypy"] = self._parse_mypy_results(mypy_dir)
        
        # Pylint results
        pylint_file = self.artifacts_dir / "python-pylint-analysis" / "pylint-report.json"
        if pylint_file.exists():
            self.report_data["python"]["pylint"] = self._parse_pylint_results(pylint_file)
        
        # Bandit security results
        bandit_file = self.artifacts_dir / "python-bandit-analysis" / "bandit-report.json"
        if bandit_file.exists():
            self.report_data["python"]["bandit"] = self._parse_bandit_results(bandit_file)
        
        # Ruff linting results
        ruff_file = self.artifacts_dir / "python-ruff-analysis" / "ruff-report.json"
        if ruff_file.exists():
            self.report_data["python"]["ruff"] = self._parse_ruff_results(ruff_file)
    
    def collect_rust_analysis(self):
        """Collect Rust static analysis results."""
        clippy_file = self.artifacts_dir / "rust-analysis" / "clippy-report.json"
        if clippy_file.exists():
            self.report_data["rust"]["clippy"] = self._parse_clippy_results(clippy_file)
    
    def collect_gdscript_analysis(self):
        """Collect GDScript analysis results."""
        gdlint_file = self.artifacts_dir / "gdscript-analysis" / "gdlint-report.txt"
        if gdlint_file.exists():
            self.report_data["gdscript"]["gdlint"] = self._parse_gdlint_results(gdlint_file)
    
    def collect_coverage_data(self):
        """Collect code coverage data."""
        
        # Python coverage
        python_coverage = self.artifacts_dir / "coverage-report" / "coverage.xml"
        if python_coverage.exists():
            self.report_data["coverage"]["python"] = self._parse_coverage_xml(python_coverage)
        
        # Rust coverage
        rust_coverage = self.artifacts_dir / "rust-coverage" / "cobertura.xml"
        if rust_coverage.exists():
            self.report_data["coverage"]["rust"] = self._parse_coverage_xml(rust_coverage)
    
    def collect_performance_data(self):
        """Collect performance analysis data."""
        benchmark_file = self.artifacts_dir / "performance-analysis" / "benchmark-results.json"
        if benchmark_file.exists():
            self.report_data["performance"]["benchmarks"] = self._parse_benchmark_results(benchmark_file)
    
    def _parse_mypy_results(self, mypy_dir: Path) -> Dict[str, Any]:
        """Parse MyPy analysis results."""
        # MyPy generates HTML reports, parse summary
        return {
            "status": "completed",
            "errors": 0,  # Would parse from HTML or use --json output
            "warnings": 0,
            "summary": "Type checking completed"
        }
    
    def _parse_pylint_results(self, pylint_file: Path) -> Dict[str, Any]:
        """Parse Pylint JSON results."""
        try:
            with open(pylint_file) as f:
                data = json.load(f)
            
            issues_by_type = {}
            for issue in data:
                issue_type = issue.get("type", "unknown")
                issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
            
            return {
                "total_issues": len(data),
                "issues_by_type": issues_by_type,
                "score": 10.0 - (len(data) * 0.1)  # Rough score calculation
            }
        except Exception:
            return {"status": "failed", "total_issues": 0}
    
    def _parse_bandit_results(self, bandit_file: Path) -> Dict[str, Any]:
        """Parse Bandit security scan results."""
        try:
            with open(bandit_file) as f:
                data = json.load(f)
            
            return {
                "total_issues": len(data.get("results", [])),
                "high_severity": len([r for r in data.get("results", []) if r.get("issue_severity") == "HIGH"]),
                "medium_severity": len([r for r in data.get("results", []) if r.get("issue_severity") == "MEDIUM"]),
                "low_severity": len([r for r in data.get("results", []) if r.get("issue_severity") == "LOW"]),
            }
        except Exception:
            return {"status": "failed", "total_issues": 0}
    
    def _parse_ruff_results(self, ruff_file: Path) -> Dict[str, Any]:
        """Parse Ruff linting results."""
        try:
            with open(ruff_file) as f:
                lines = f.readlines()
            
            issues = [json.loads(line) for line in lines if line.strip()]
            
            rules_violated = {}
            for issue in issues:
                rule = issue.get("code", "unknown")
                rules_violated[rule] = rules_violated.get(rule, 0) + 1
            
            return {
                "total_issues": len(issues),
                "rules_violated": rules_violated,
                "most_common_rule": max(rules_violated.items(), key=lambda x: x[1]) if rules_violated else None
            }
        except Exception:
            return {"status": "failed", "total_issues": 0}
    
    def _parse_clippy_results(self, clippy_file: Path) -> Dict[str, Any]:
        """Parse Rust Clippy results."""
        try:
            with open(clippy_file) as f:
                lines = f.readlines()
            
            warnings = []
            errors = []
            
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("message", {}).get("level") == "warning":
                        warnings.append(data)
                    elif data.get("message", {}).get("level") == "error":
                        errors.append(data)
                except json.JSONDecodeError:
                    continue
            
            return {
                "warnings": len(warnings),
                "errors": len(errors),
                "total_issues": len(warnings) + len(errors)
            }
        except Exception:
            return {"status": "failed", "total_issues": 0}
    
    def _parse_gdlint_results(self, gdlint_file: Path) -> Dict[str, Any]:
        """Parse GDScript linting results."""
        try:
            with open(gdlint_file) as f:
                content = f.read()
            
            # Simple parsing of gdlint output
            lines = content.split('\n')
            issues = [line for line in lines if 'Error:' in line or 'Warning:' in line]
            
            return {
                "total_issues": len(issues),
                "status": "completed"
            }
        except Exception:
            return {"status": "failed", "total_issues": 0}
    
    def _parse_coverage_xml(self, coverage_file: Path) -> Dict[str, Any]:
        """Parse XML coverage reports."""
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            # Parse coverage percentage
            coverage_elem = root.find('.//coverage')
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get('line-rate', 0))
                branch_rate = float(coverage_elem.get('branch-rate', 0))
                
                return {
                    "line_coverage": round(line_rate * 100, 2),
                    "branch_coverage": round(branch_rate * 100, 2),
                    "overall_coverage": round((line_rate + branch_rate) / 2 * 100, 2)
                }
            
            return {"status": "no_data"}
        except Exception:
            return {"status": "failed"}
    
    def _parse_benchmark_results(self, benchmark_file: Path) -> Dict[str, Any]:
        """Parse performance benchmark results."""
        try:
            with open(benchmark_file) as f:
                data = json.load(f)
            
            benchmarks = data.get("benchmarks", [])
            if benchmarks:
                avg_time = sum(b.get("stats", {}).get("mean", 0) for b in benchmarks) / len(benchmarks)
                return {
                    "total_benchmarks": len(benchmarks),
                    "average_execution_time": round(avg_time, 4),
                    "status": "completed"
                }
            
            return {"status": "no_benchmarks"}
        except Exception:
            return {"status": "failed"}
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        score = 100.0
        
        # Deduct points for issues
        python_issues = (
            self.report_data["python"].get("pylint", {}).get("total_issues", 0) +
            self.report_data["python"].get("bandit", {}).get("total_issues", 0) +
            self.report_data["python"].get("ruff", {}).get("total_issues", 0)
        )
        
        rust_issues = self.report_data["rust"].get("clippy", {}).get("total_issues", 0)
        gdscript_issues = self.report_data["gdscript"].get("gdlint", {}).get("total_issues", 0)
        
        total_issues = python_issues + rust_issues + gdscript_issues
        score -= min(total_issues * 0.5, 30)  # Cap deduction at 30 points
        
        # Bonus for good coverage
        python_coverage = self.report_data["coverage"].get("python", {}).get("line_coverage", 0)
        rust_coverage = self.report_data["coverage"].get("rust", {}).get("line_coverage", 0)
        
        avg_coverage = (python_coverage + rust_coverage) / 2 if python_coverage and rust_coverage else max(python_coverage, rust_coverage)
        if avg_coverage > 80:
            score += 5
        elif avg_coverage > 60:
            score += 2
        
        return max(score, 0)
    
    def generate_markdown_report(self) -> str:
        """Generate markdown quality report."""
        quality_score = self.calculate_quality_score()
        
        # Determine grade
        if quality_score >= 90:
            grade = "A+"
            emoji = "🟢"
        elif quality_score >= 80:
            grade = "A"
            emoji = "🟢"
        elif quality_score >= 70:
            grade = "B"
            emoji = "🟡"
        elif quality_score >= 60:
            grade = "C"
            emoji = "🟠"
        else:
            grade = "D"
            emoji = "🔴"
        
        report = f"""# 🔍 AI Game Development Ecosystem - Quality Report

## {emoji} Overall Quality Score: {quality_score:.1f}/100 (Grade: {grade})

## 📊 Language-Specific Analysis

### 🐍 Python Analysis
"""
        
        # Python section
        python_data = self.report_data["python"]
        if python_data:
            pylint = python_data.get("pylint", {})
            bandit = python_data.get("bandit", {})
            ruff = python_data.get("ruff", {})
            
            report += f"""
- **Pylint**: {pylint.get('total_issues', 0)} issues found
- **Bandit Security**: {bandit.get('total_issues', 0)} security issues ({bandit.get('high_severity', 0)} high severity)
- **Ruff Linting**: {ruff.get('total_issues', 0)} style/quality issues
"""
        
        # Rust section
        rust_data = self.report_data["rust"]
        report += f"""
### 🦀 Rust Analysis
"""
        if rust_data:
            clippy = rust_data.get("clippy", {})
            report += f"""
- **Clippy**: {clippy.get('warnings', 0)} warnings, {clippy.get('errors', 0)} errors
"""
        
        # GDScript section
        gdscript_data = self.report_data["gdscript"]
        report += f"""
### 🎮 GDScript Analysis
"""
        if gdscript_data:
            gdlint = gdscript_data.get("gdlint", {})
            report += f"""
- **GDLint**: {gdlint.get('total_issues', 0)} issues found
"""
        
        # Coverage section
        coverage_data = self.report_data["coverage"]
        report += f"""
## 📈 Code Coverage

"""
        if coverage_data:
            python_cov = coverage_data.get("python", {})
            rust_cov = coverage_data.get("rust", {})
            
            if python_cov.get("line_coverage"):
                report += f"- **Python**: {python_cov['line_coverage']:.1f}% line coverage\n"
            if rust_cov.get("line_coverage"):
                report += f"- **Rust**: {rust_cov['line_coverage']:.1f}% line coverage\n"
        
        # Performance section
        performance_data = self.report_data["performance"]
        if performance_data.get("benchmarks"):
            benchmarks = performance_data["benchmarks"]
            report += f"""
## ⚡ Performance Analysis

- **Benchmarks**: {benchmarks.get('total_benchmarks', 0)} tests completed
- **Average Execution Time**: {benchmarks.get('average_execution_time', 0):.4f}s
"""
        
        # Recommendations
        report += """
## 🎯 Recommendations

"""
        recommendations = []
        
        if quality_score < 80:
            recommendations.append("- Focus on reducing linting issues across all languages")
        
        python_coverage = coverage_data.get("python", {}).get("line_coverage", 0)
        if python_coverage < 80:
            recommendations.append("- Increase Python test coverage to at least 80%")
        
        security_issues = self.report_data["python"].get("bandit", {}).get("total_issues", 0)
        if security_issues > 0:
            recommendations.append("- Address security issues identified by Bandit")
        
        if not recommendations:
            recommendations.append("- Great work! All quality metrics are within acceptable ranges")
        
        report += "\n".join(recommendations)
        
        report += """

---
*This report was automatically generated by the AI Game Development Ecosystem quality analysis pipeline.*
"""
        
        return report
    
    def generate_html_report(self) -> str:
        """Generate HTML quality report with charts."""
        markdown_content = self.generate_markdown_report()
        
        # Simple HTML wrapper (could be enhanced with charts using Chart.js)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Game Dev Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div id="content">
        {markdown_content.replace('#', '<h1>').replace('##', '</h1><h2>').replace('###', '</h2><h3>').replace('\n', '<br>')}
    </div>
</body>
</html>
"""
        return html
    
    def run(self):
        """Execute the quality report generation."""
        print("🔍 Collecting analysis results...")
        
        self.collect_python_analysis()
        self.collect_rust_analysis()
        self.collect_gdscript_analysis()
        self.collect_coverage_data()
        self.collect_performance_data()
        
        print("📊 Generating quality report...")
        
        # Generate reports
        markdown_report = self.generate_markdown_report()
        html_report = self.generate_html_report()
        
        # Write reports
        with open("quality-report.md", "w") as f:
            f.write(markdown_report)
        
        with open("quality-report.html", "w") as f:
            f.write(html_report)
        
        print("✅ Quality report generated successfully!")
        print(f"📄 Markdown: quality-report.md")
        print(f"🌐 HTML: quality-report.html")


if __name__ == "__main__":
    generator = QualityReportGenerator()
    generator.run()