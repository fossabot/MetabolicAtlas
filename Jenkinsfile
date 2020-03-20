pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh '''
          cp /var/lib/jenkins/postgres.env .
          echo "VUE_APP_MATOMOID=14" >> frontend/.env.production
        '''
        echo 'Copied PostgreSQL and Django environments. Configured Vue environment.'
        withCredentials([string(credentialsId: 'f8066a74-2a9c-4510-8bd5-7edb569fff14', variable: 'human1db'), string(credentialsId: '7650c2ee-c69d-4499-a180-b089acfd1afc', variable: 'yeast8db'), string(credentialsId: '	5013ec59-acd1-4b13-a0c2-90904f2aceb1', variable: 'gemsdb')]) {
          sh '''
            wget $human1db -O human1.db
            wget $gemsdb -O gems.db
            wget $yeast8db -O yeast8.db
          '''
        }
        echo 'Downloaded source databases.'
      }
    }
    stage('Build') {
      steps {
        sh '''
          . proj.sh production
          build-stack --build-arg SERVER_NAME=icsb.chalmers.se --build-arg USE_IP_FILTER=true
        '''
        echo 'Built new Docker images.'
      }
    }
    stage('Cleanup running containers') {
      steps {
        sh '''
          . ./proj.sh production
          clean-stack
        '''
        echo 'Stopped active Docker containers and deleted Docker volumes. Needed only when there are database content changes, which requires deleting the Postgres volume.'
      }
    }
    stage('Run') {
      steps {
        sh '''
          . ./proj.sh production
          start-stack
        '''
        echo 'Running the new Docker images.'
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          . ./proj.sh production
          db-import human1.db
          db-import yeast8.db
          db-import gems.db
          db-make-migrations
          db-migrate yeast8 --fake
          db-migrate human1 --fake
          db-migrate gems --fake
        '''
      }
    }
    stage('Clean up') {
      steps {
        sh '''
          docker rmi $(docker images -q) --force || true
          rm *.db
        '''
        echo 'Deleted old Docker images and containers. We are live!'
      }
    }
  }
}
