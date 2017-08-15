# thor-certbot-scripts
Scripts for creating and updating letsencrypt certs.

==make_ssl_proxy.py==
This script obtains a cert for a new domain. These domains will be proxied to a given ip-address of an lxc-container.

It generates a config file for a proxy server for a container.
Next it enables a http server to let letsencrypt authenticate the domain.
Then a certificate is obtained and installed.
Finally the temporary server is deleted and the final config is placed, and nginx is reloaded.
The config uses a lot of includes from /etc/nginx/snippets")

==get_server_names.py==
This script parses an nginx server config file and prints all its server names in certbot command style.
This can be used to update an existing letsencrypt cert with more domain names.

To add a extra domain to an existing cert, add the domain to the server names in /etc/nginx/sitesn_enabled/<name> and reload nginx
Then just rerun certbot with the old AND new domains with the '-d' flag. Get these names directly by running get_server_names.py
To expand eir.thor.edu to eir.thor.edu and ma-eir.nl use


certbot certonly -n --webroot -w /var/www/web_eir -d eir.thor.edu -d ma-eir.nl
