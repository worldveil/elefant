import time
import os
import subprocess

from boto.s3.key import Key
import boto


class Elefant(object):
	"""
	Allows you to backup and restore your Heroku database
	using your own private storage in S3. This allow circumventing
	the backup limit in Heroku plans and also gives peace of mind 
	that your data is backed up somewhere else besides Heroku.

	Tested on Postgres 9.4.

	Usage: 
	- Ensure AWS credentials are set up in environment variables
	- Ensure heroku is logged in with $ heroku login 
	"""
	CommandMake        = 'heroku pg:backups capture --app %s'
	CommandDownload    = 'curl -o %s `heroku pg:backups public-url %s --app %s`'
	CommandDelete      = 'heroku pg:backups delete %s --app %s --confirm %s'
	CommandRestore     = 'PGPASSWORD=%(password)s pg_restore --verbose --clean --no-acl --no-owner -n public -h %(host)s -U %(username)s -d %(database)s -p %(port)d %(dump)s'
	CommandCredentials = 'heroku pg:credentials DATABASE_URL'

	NameToken		   = '---backup--->'
	UrlToken		   = 'postgres://'

	DumpPath           = 'latest.dump'
	RestorePath        = 'restore.dump'
	HomeEnvName		   = 'HOME'

	DateFormat         = '%Y_%m_%d-%H_%M_%S'
	BackupFormat       = '%(app)s__%(date)s.dump'

	def __init__(self, app, bucket, env=None, region=None):
		self.env = env or {}
		self.app = app
		self.region = region or 'us-east-1'
		self.bucket = bucket

		# additional env variables
		self.env.update({
			Elefant.HomeEnvName : os.path.expanduser("~"),
		})

	def run(self, cmd):
		return subprocess.check_output(cmd, env=self.env, shell=True)

	def backup(self):
		bid = self.create()
		self.download(bid)
		self.save()
		self.delete(bid)

	def create(self):
		cmd = Elefant.CommandMake % self.app
		output = self.run(cmd)
		for line in output.split('\n'):
			if Elefant.NameToken in line:
				content = line.split(">")[-1]
				print "Created backup: %s" % content.strip()
				return content.strip()

	def download(self, backup_id):
		print "Downloading %s..." % backup_id
		cmd = Elefant.CommandDownload % (
			Elefant.DumpPath, backup_id, self.app)
		self.run(cmd)

	def connect(self):
		s3 = boto.s3.connect_to_region(self.region)
		try:
			bucket = s3.get_bucket(self.bucket)
		except boto.exception.S3ResponseError:
			# bucket doesn't exist, let's create it
			# this will fail if bucket name already taken 
			# or user doesn't have correct permissions
			bucket = s3.create_bucket(self.bucket)
		return s3, bucket

	def save(self):
		name = self.name()
		print "Saving from %s to %s..." % (Elefant.DumpPath, name)
		s3, bucket = self.connect()
		key = Key(bucket=bucket, name=name)
		key.set_contents_from_filename(Elefant.DumpPath)

	def delete(self, backup_id):
		print "Deleting..."

		# delete from heroku
		cmd = Elefant.CommandDelete % (
			backup_id, self.app, self.app)
		self.run(cmd)

		# then delete locally
		cmd = "rm %s" % Elefant.DumpPath
		self.run(cmd)

	def name(self):
		date = time.strftime(Elefant.DateFormat)
		return Elefant.BackupFormat % {
			"app" : self.app,
			"date" : date,}

	@property
	def backups(self):
		s3, bucket = self.connect()
		return list(bucket.list())

	def restore(self, backup_key):
		# get the database backup
		s3, bucket = self.connect()
		if isinstance(backup_key, boto.s3.key.Key):
			assert backup_key in bucket, "Cannot restore from key outside S3Bucket (%s)!" % S3Bucket
		else:
			backup_key = Key(bucket=bucket, name=backup_key)
		
		# download to disk
		backup_key.get_contents_to_filename(Elefant.RestorePath)

		# get the credentials for heroku postgres
		cmd = Elefant.CommandCredentials
		output = self.run(cmd)

		# extract credentials
		credentials = {}
		for line in output.split('\n'):
			if Elefant.UrlToken in line:
				url = line.strip()
				credentials = self.extract_postgres_url(url)
				break

		# apply the restore
		credentials.update({'dump' : Elefant.RestorePath})
		cmd = Elefant.CommandRestore % credentials
		try:
			print self.run(cmd)
		except subprocess.CalledProcessError as e:
			# Some warnings associated with pg_restore
			# can be ignored (harmless), but consult the docs
			print "PROCESS ERROR CAUGHT:", e

		# delete the local restore file
		print self.run("rm %s" % Elefant.RestorePath)

	def extract_postgres_url(self, url):
		"""
		Format:
			postgres://username:password@localhost/myrailsdb
		"""
		colon_parts = url.split(':')
		at_parts = colon_parts[2].split('@')
		slash_parts = colon_parts[3].split('/')

		username = colon_parts[1][2:]
		password = at_parts[0]
		host = at_parts[1]
		database = slash_parts[1]

		try:
			port = int(slash_parts[0])
		except ValueError:
			port = 5432

		return {
			"username" : username,
			"password" : password,
			"host" : host,
			"database" : database,
			"port" : port,
		}

	def __repr__(self):
		return "<Elefant: %s>" % self.app
