
Get the MolStar code as submodule

```
git submodule add https://github.com/molstar/molstar.git
```

Model Server

https://github.com/molstar/molstar/tree/master/docs/model-server

Install npm deps

```
npm install
npm install -g ts forever http-server 
```

Edit config

```
vim src/server/model/config.ts
```

Build molstar

```
NODE_ENV=production npm run build
```

Run server to see molstar app

```
http-server -p 9000
```

Add files

```
node build\node_modules\servers\model\preprocess -i input.cif -oc output.cif -ob output.bcif --cfg config.json
```

---

Maxit (mmCIF / PDB converter)

Download, unpack, build

```
wget https://sw-tools.rcsb.org/apps/MAXIT/maxit-v10.100-prod-src.tar.gz
tar -zxvf maxit-v10.100-prod-src.tar.gz
cd maxit-v10.100-prod-src
make binary
```

```
$ RCSBROOT=./maxit-v10.100-prod-src
$ maxit-v10.100-prod-src/bin/maxit
Usage: maxit-v10.100-prod-src/bin/maxit -input inputfile -output outputfile -o num [ -log logfile ]
  [-o  1: Translate PDB format file to CIF format file]
  [-o  2: Translate CIF format file to PDB format file]
  [-o  8: Translate CIF format file to mmCIF format file]

```