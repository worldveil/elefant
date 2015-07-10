from elefant import Elefant


# create Elefant object, passing in the Heroku app name
hb = Elefant(app="myapp", bucket="mybucket")

print "Making and backup and uploading to S3..."
hb.backup() 

print "Availiable backups:"
backups = hb.backups 
for b in backups: 
	print b.name

print "Restoring from most recent backup..."
hb.restore(b) 

print "Restoring from most recent backup using a string..."
hb.restore(b.name)