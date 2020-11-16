from argparse import ArgumentParser
from datetime import datetime
import json,sys
import jinja2
import os
import uuid
import ntpath
import math

class TwistlockReporter():
    def __init__(self,filename,output,template):
        if not os.path.exists(template):
            raise Exception("Template:{} not found.".format(template))

        if not os.path.exists(filename):
            raise Exception("Twistlock JSON output:{} not found.".format(filename))

        now = datetime.today().strftime('%Y-%m-%d')
        uuid = self.generate_uuid()[:5]
        self.report_filename = "{}_{}.html".format(uuid,now)

        self.twistlock_output = filename # twistlock json results
        self.output_folder = output # output dir of html report
        self.template_dir = ntpath.dirname(template) # template dir
        self.template_filename = ntpath.basename(template) # jinja template

        if not os.path.isdir(self.output_folder): # make output folder if not exist
            os.mkdir(self.output_folder)

        self.abs_filename = os.path.join(self.output_folder,self.report_filename) # abs of html report

    def get_time(self):
        return str(round(datetime.now().timestamp()))

    def generate_uuid(self):
        return uuid.uuid4().hex

    def generate_html(self,data):
        report = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir)).get_template(self.template_filename).render(data=data)
        with open(self.abs_filename,"w") as file:
            file.write(report)
        return {"message":"ok","file_name":self.report_filename,"full_path":self.abs_filename,"success":True}

    def create_twistlock_report(self):
        '''Get summary of a team'''
        data = {}

        output = self.parse_twistlock_image_scan()

        data["data"] = output
        return self.generate_html(data)

    def humanize_bytes(self,size_bytes):
       if size_bytes == 0:
           return "0B"
       size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
       i = int(math.floor(math.log(size_bytes, 1024)))
       p = math.pow(1024, i)
       s = round(size_bytes / p, 2)
       return s,size_name[i]

    def parse_twistlock_image_scan(self):
        with open(self.twistlock_output) as f:
            total_size = 0
            content = json.loads(f.read())
            data = {
                "meta":{},
                "history":[],
                "vulnerabilities":{"critical":[],"high":[],"medium":[],"low":[]},
                "compliance":{"critical":[],"high":[],"medium":[],"low":[]}
            }

            for scan in content:
                # collect metadata of the scan
                for key in ["pass","jobName","build","time","version","_id"]:
                    if key in scan:
                        data["meta"][key] = scan[key]

                meta_keys = ["distro","osDistro","labels","vulnerabilityRiskScore","trustStatus","complianceRiskScore","id",
                    "osDistroVersion","complianceIssuesCount","osDistroRelease","complianceDistribution","riskFactors",
                    "Secrets","vulnerabilityDistribution","repoDigests","layers"]
                for key in meta_keys:
                    if key in scan["entityInfo"]:
                        data["meta"][key] = scan["entityInfo"][key]

                # get binary count
                data["meta"]["binary_count"] = len(scan["entityInfo"].get("binaries",[]))

                # get size and history
                if "image" in scan["entityInfo"]:
                    for layer in scan["entityInfo"]["image"].get("history",[]):
                        if "sizeBytes" in layer:
                            total_size += layer["sizeBytes"]
                            layer_size,layer_abbr = self.humanize_bytes(layer["sizeBytes"])
                            layer["humanize_size"] = "{} {}".format(layer_size,layer_abbr)
                        layer["action"] = layer.get("instruction","").split(" ")[0]
                        data["history"].append(layer)
                size,abbr = self.humanize_bytes(total_size)
                data["meta"]["total_size"] = size
                data["meta"]["size_abbr"] = abbr

                # get compliance violations
                for record in scan["entityInfo"].get("complianceIssues",[]):
                    data["compliance"][record["severity"]].append(record)

                # get vulnerability violations
                for record in scan["entityInfo"].get("vulnerabilities",[]):
                    if record.get("status") == "open":
                        record["remediation"] = "There is not a published fix as of {}".format(record.get("discovered"))
                    else:
                        record["remediation"] = "There is a fix available: {}. See Description for more information and/or {}".format(record["status"],record.get("link"))
                    data["vulnerabilities"][record["severity"]].append(record)
                return data

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                    help="json file from prisma cloud")
    parser.add_argument("-o", "--output", dest="output",
                    help="desired destination directory for the html report")
    parser.add_argument("-t", "--template", dest="template",
                    help="absolute path to the jinja template")

    args = parser.parse_args()

    '''Example
    script.py --file /path-to/prisma-cloud-scan-results.json --output /path-to/output-folder --template /path-to/template-file

    JSON file generated by Twistlock Jenkins plugin or via cli:
    ./twistcli images scan --token=$TL_TOKEN --address=https://us-west1.cloud.twistlock.com/us-3-159214902 --ci --ci-results-file prisma-cloud-scan-results.json 017e5c383867
    '''
    report = TwistlockReporter(args.filename,args.output,args.template)
    #report.parse_twistlock_image_scan()
    #print(json.dumps(report.parse_twistlock_image_scan(),indent=4))
    report.create_twistlock_report()
