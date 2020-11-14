# videogenerators setup on VM

- IP: 77.68.89.122
- ssh root@77.68.89.122
- FastHost Credentials
    - ckayay@gmail.com
    - G@nghis100
- Server Credentials
    - root
    - $7#*Uj16c3
- Install Ubuntu
- Add entry to /etc/hosts file for domain name
- Install Webmin - https://www.digitalocean.com/community/tutorials/how-to-install-webmin-on-ubuntu-20-04
    - Webmin Credentials are same as server credentials
- Install Apache
    - sudo apt-get install apache2
    - sudo a2enmod ssl
    - cd /etc/apache2/sites-enabled
    - sudo a2ensite default-ssl
    - sudo /etc/init.d/apache2 restart

- SSL Setup
    - openssl genrsa -des3 -out www.videogenerators.com.key.pem 2048 (pass:$7#*Uj16c3)
    - openssl req -new -key www.videogenerators.com.key.pem -out www.videogenerators.com.csr

- Get Latest code
    - git clone https://github.com/ckayay/videogenerators.git

- Install React
    - sudo apt-get install curl
    - curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    - sudo apt-get install -y nodejs
    - sudo npm install npm@latest -g
    - npm install -g create-react-app
    - npx create-react-app videogenapp
    - npm install mic-recorder
    - npm install pm2 -g
  
  - Package react app
    - npm start build
    - cp -r build/* /var/www/html/
    
- Install Flask
    - sudo apt-get install libapache2-mod-wsgi python-dev
    - sudo a2enmod wsgi 
    - sudo apt-get install python-pip 
    - sudo pip install Flask 
    
 - Start Flask
    - nohup python app_flask.py
    - enter pass
    - bg %1
  
  - Configure Apache
  - Default SSL.conf:
    <IfModule mod_ssl.c>
        <VirtualHost _default_:443>

                ServerName videogenerators.com
                ServerAdmin webmaster@localhost

                WSGIDaemonProcess flaskapp user=www-data group=www-data threads=5 python-home=/var/www/flaskapp/flaskapp/venv
                WSGIProcessGroup flaskapp
                WSGIScriptAlias /api /var/www/flaskapp/flaskapp.wsgi

                DocumentRoot /var/www/html

           
                ErrorLog ${APACHE_LOG_DIR}/error.log
                CustomLog ${APACHE_LOG_DIR}/access.log combined

                #   SSL Engine Switch:
                #   Enable/Disable SSL for this virtual host.
                SSLEngine on
                # SSLCertificateFile    /etc/ssl/certs/ssl-cert-snakeoil.pem
                # SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
                SSLCertificateFile      /home/cert/083CD4A5C4AE3AA3B896925B2165069D.cer
                SSLCertificateKeyFile /home/cert/www.videogenerators.com.key.pem
                SSLCertificateChainFile /home/cert/083CD4A5C4AE3AA3B896925B2165069D.cer
                
                                <FilesMatch "\.(cgi|shtml|phtml|php)$">
                                SSLOptions +StdEnvVars
                </FilesMatch>

                <Directory /var/www/html/>
                        Order allow,deny
                        Allow from all
                </Directory>

                <Directory /var/www/flaskapp/flaskapp/>
                        Order allow,deny
                        Allow from all
                </Directory>

                <Directory /usr/lib/cgi-bin>
                                SSLOptions +StdEnvVars
                </Directory>
                
         </VirtualHost>
   </IfModule>
   
   - Deploy React App to Apache
    - https://medium.com/@kayode.adechinan/host-react-application-on-apache-server-90c803241483
