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
            //image: customImage,
            image: "${group}_${service}",
            key: '',
            logLevel: 'info',
            podmanPath: '',
            project: '',
            resultsFile: 'prisma-cloud-scan-results.json',
            ignoreImageBuildTime:true
        }
    }
  }
}
