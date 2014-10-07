# AWS security group dependency finder

list AWS security group dependencies
 
------

# requirements

Python 2.7+ and boto installed. you can install boto by:
```
pip install boto
```

# Install

download the single file, 

# configure 

setup your boto credentails.

here's a few options:
     setup environment varialbes: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
     or create one or some of below files (boto will evaluate in order):
        /etc/boto.cfg
        ~/.boto
        ~/.aws/credentials 
     and put your credentials in the file(s) with below format:
       [Credentials]
       aws_access_key_id = <your_access_key_here>
       aws_secret_access_key = <your_secret_key_here>

# usage:

``` 
python sgdeps.py --region <region_name> security_group
```

# example:

```
$ python sgdeps.py --region us-east-1 mingbotest-A
sg-b4566ad1 (mingbotest-A)
|-- sg-9b566afe (mingbotest-C2)
|-- sg-9f566afa (mingbotest-C1)
|  |-- sg-69576b0c (mingbotest-D2)
|  |  `-- sg-b4566ad1 (mingbotest-A) ** loop
|  `-- sg-64576b01 (mingbotest-D1)
|     `-- sg-9b566afe (mingbotest-C2)
|-- sg-8b566aee (mingbotest-B2)
`-- sg-86566ae3 (mingbotest-B1)
```
