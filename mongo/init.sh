#!/bin/bash
# Wait for MongoDB to be ready
until mongosh --eval "print(\"waited for connection\")"
do
    sleep 5
done

mongosh <<EOF
rs.initiate(
  {
    _id: "rs0",
    members: [
      { _id: 0, host: "mongo1:27017" },
      { _id: 1, host: "mongo2:27017" },
      { _id: 2, host: "mongo3:27017" }
    ]
  }
)
EOF