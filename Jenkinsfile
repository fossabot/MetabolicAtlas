pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh '''cp /var/lib/jenkins/postgres.env .'''
        echo 'Copied PostgreSQL and Django environment.'
        sh '''
          sed -i "s/svgMapURL:.*/svgMapURL: 'https:\\/\\/ftp.metabolicatlas.org\\/.maps',/g"  frontend/src/components/explorer/mapViewer/Svgmap.vue
        '''
      }
    }
    stage('Build') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker volume prune --force || true
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml build
        '''
        echo 'Built new Docker images.'
      }
    }
    stage('Cleanup old Docker setup') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker rm $(docker ps -a -q) || true
          docker volume prune --force || true
        '''
        echo 'Deleted old Docker containers and volumes.'
      }
    }
    stage('Run') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d
        '''
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          wget https://chalmersuniversity.box.com/shared/static/ux9bnfyycig8qgxtayjnjnczqt7b92b7.db -O human1.db
          wget https://chalmersuniversity.box.com/shared/static/om86nb6y8ji044wzoiljm8aghmbdvs41.db -O gems.db
          wget https://chalmersuniversity.box.com/shared/static/n3izn3hkp1hmmgodpxaczpkqd0p64ngf.db -O yeast8.db

          docker exec -i db psql -U postgres < human1.db
          docker exec -i db psql -U postgres < yeast8.db
          docker exec -i db psql -U postgres < gems.db

          docker exec backend python manage.py makemigrations
          docker exec backend python manage.py migrate --database yeast8 --fake
          docker exec backend python manage.py migrate --database human1 --fake
          docker exec backend python manage.py migrate --database gems --fake
        '''
      }
    }
    stage('Clean up') {
      steps {
        sh '''
          docker rm $(docker ps -a -q) || true
          docker rmi $(docker images -q) --force || true
          rm *.db
        '''
        echo 'Deleted old Docker images. We are live!'
      }
    }
  }
}
