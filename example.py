from elefant import Elefant

# create Elefant object, passing in the Heroku app name and backups bucket
eft = Elefant("myapp", "mybucket", prefix="/dev/sda1")

print "Making backup, uploading to S3, and then deleting from Heroku..."
eft.backup() 

print "Availiable backups:"
backups = eft.backups 
for b in backups: 
	print b.name

print "Restoring from most recent backup..."
eft.restore(b) 

print "Restoring (this time using the name of the S3 filename key)..."
eft.restore(b.name)