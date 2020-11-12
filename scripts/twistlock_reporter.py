from argparse import ArgumentParser
from datetime import datetime
import json,sys
import jinja2
import os
import uuid
import ntpath

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

    def parse_twistlock_image_scan(self):
        with open(self.twistlock_output) as f:
            content = json.loads(f.read())
            for scan in content:
                data = {"meta":{},"critical":[],"high":[],"medium":[],"low":[]}

                # collect metadata of the scan
                for key in ["pass","jobName","entityInfo","build","time","version","_id"]:
                    data["meta"][key] = scan[key]

                for record in scan["entityInfo"]["vulnerabilities"]:
                    # filter on record key/values here
                    ''' Example:
                        print(record["severity"])
                        print(record["exploit"])
                        print(record["cvss"])
                        print(record["description"])
                    '''
                    # add record to top-level dictionary
                    data[record["severity"]].append(record)
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
    '''
    report = TwistlockReporter(args.filename,args.output,args.template)
    report.create_twistlock_report()

