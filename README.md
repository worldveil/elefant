elefant
---

Allows you to backup and restore your Heroku database using your own private storage in S3. This allows circumventing the backup limit in Heroku plans and also gives peace of mind that your data is backed up somewhere else besides Heroku.

Tested only on Unix machines and Heroku Postgres 9.4.

## Installation

```bash
pip install elefant
```

Elefant's only dependencies are [`boto`](https://boto.readthedocs.org/en/latest/) in Python and, of course, `postgres` (use of `pg_restore`).

## Usage

Steps:

* Ensure AWS credentials are set up in environment variables for `boto`
* Ensure heroku is logged in with $ heroku login

Elefant will create an S3 bucket for you so long as it is not taken and your AWS user has the permissions to do so.

## Backup Format

You'll give `Elephant` both the name of your S3 bucket and the name of your Heroku app upon instantiation, and it will in turn store backup dumps with the following format:

	<S3-BUCKET>/<HEROKU-APP-NAME>__%Y_%m_%d-%H_%M_%S.dump

where the formatting is [standard Python date formatting](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior).

The filetype is a Postgres dump file, not a SQL text dump. 

## Example 

```python
from elefant import Elefant

# create Elefant object, passing in the Heroku app name and backups bucket
eft = Elefant("myapp", "mybucket")

print "Making backup, uploading to S3, and then deleting from Heroku..."
eft.backup() 

print "Availiable backups:"
backups = eft.backups 
for b in backups: 
	print b.name

print "Restoring from most recent backup..."
eft.restore(b) 

print "Restoring from most recent backup using a string..."
eft.restore(b.name)
```