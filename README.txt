i've had to install a few libraries to make this work
You'll probably have to install them yourself and repeat the install occaisionally

of course you will need to extract the .zip file or it will break

1. Open CMD
2. Run cd C:\[your username].PAKURANGA\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64\Scripts
3. Run pip3.7 install -U pygame --user
4. Run pip3.7 install -U pymunk --user
5. Run program and enter your pakuranga username - this is needed as pip will install the libraries in the wrong site-packages folder and the program needs to add the wrong folder to the path, found in your user folder

this still might not work because school computers are weird