from elefant import Elefant

# create Elefant object, passing in the Heroku app name and backups bucket
hb = Elefant("myapp", "mybucket")

print "Making backup, uploading to S3, and then deleting from Heroku..."
hb.backup() 

print "Availiable backups:"
backups = hb.backups 
for b in backups: 
	print b.name

print "Restoring from most recent backup..."
hb.restore(b) 

print "Restoring (this time using the name of the S3 filename key)..."
hb.restore(b.name)