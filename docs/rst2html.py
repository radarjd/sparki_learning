import sys
import docutils.core

if len(sys.argv) < 3:
    print("usage: {} <src> <dst>".format(sys.argv[0]))
    sys.exit(2)
    
print("Converting rst file {} to html file {}".format(sys.argv[1], sys.argv[2]))
    
docutils.core.publish_file( 
    source_path = sys.argv[1], 
    destination_path = sys.argv[2], 
    writer_name ="html")

print("Done!")
