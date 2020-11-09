def group = "secops"
def service = "hello-flask"

pipeline {
  //checkout scm
  //agent { dockerfile true }
  agent any
  stages {
    stage("Build Image") {
      steps {
        script {
          def customImage = docker.build("${group}_${service}")
        }
      }
    }
    stage('Scan') {
        steps {
            // Scan the image
            prismaCloudScanImage ca: '',
            cert: '',
            dockerAddress: 'unix:///var/run/docker.sock',
            image: "${group}_${service}",
            key: '',
            logLevel: 'debug',
            podmanPath: '',
            project: '',
            resultsFile: 'prisma-cloud-scan-results.json',
            ignoreImageBuildTime:true
        }
    }
    stage('Parse') {
      steps {
        sh '/usr/bin/python3 /home/bmarsh/test.py prisma-cloud-scan-results.json'
      }
    }
  }
//  post {
//      always {
//          prismaCloudPublish resultsFilePattern: 'prisma-cloud-scan-results.json'
//      }
//  }
}
