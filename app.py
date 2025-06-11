from flask import Flask, render_template, request
from pabutools.rules.gpseq import gpseq
from pabutools.election.instance import Instance, Project
from pabutools.election.profile import ApprovalProfile
from pabutools.election.ballot.approvalballot import ApprovalBallot
import io
import sys
import logging
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    logs = ""

    if request.method == "POST":
        try:
            budget = float(request.form["budget"])
            raw_projects = request.form["projects"].strip().split("\n")
            raw_profile = request.form["profile"].strip().split("\n")

            projects = []
            for line in raw_projects:
                name, cost = line.strip().split(",")
                projects.append(Project(name.strip(), float(cost.strip())))

            instance = Instance(projects, budget)

            profile = []
            for line in raw_profile:
                indices = list(map(int, line.strip().split(",")))
                ballot = ApprovalBallot([projects[i] for i in indices])
                profile.append(ballot)

            approval_profile = ApprovalProfile(profile)

            # ✅ Capture logs BEFORE running gpseq
            buffer = io.StringIO()

            # Create handler for logging to string
            log_handler = logging.StreamHandler(buffer)
            log_handler.setLevel(logging.DEBUG)

            # Optional: custom formatter
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            log_handler.setFormatter(formatter)

            # Attach handler to root logger
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)  # to capture debug logs
            logger.addHandler(log_handler)

            print("Starting GPseq execution...")
            selected = gpseq(instance, approval_profile)
            log_handler.flush()
            logs = buffer.getvalue()
            logger.removeHandler(log_handler)
            print("Execution complete.")

            result = [p.name for p in selected]

            sys.stdout = sys.__stdout__
            logs = buffer.getvalue()

        except Exception as e:
            sys.stdout = sys.__stdout__
            error = str(e)

    return render_template("index.html", result=result, error=error, logs=logs)
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/paper")
def paper():
    return render_template("paper.html")

if __name__ == "__main__":
    app.run(debug=True)
