pragma Singleton
import QtQuick
import fsearch

QtObject {

    property var pendingRequests: ({})

    function addRecurringFile(path) {
        AsyncRequest.request({
            command: "sql_command",
            sql: `INSERT OR IGNORE INTO recurring_files (file_path) VALUES ('${path}')`
        }).then(function (results) {}).catch(function (error) {
            console.log("error adding rec file: " + error);
        });
    }

    function urlToPath(fileUrl) {
        // Convert file URL to local path
        var path = fileUrl.toString().replace(/^file:\/\/\//, '')
        
        // On Windows, replace forward slashes with backslashes
        if (Qt.platform.os === "windows") {
            path = path.replace(/\//g, '\\')
        }
        
        return path
    }

    function insertRecord(table, column_names: var, values: var) {

        AsyncRequest.request({
            command: "sql_command",
            sql: `INSERT`,
            table:table,
            column_names:column_names,
            values:values
        }).then(function (results) {
            // console.log("Record inserted successfully");
            // Handle success if needed
        }).catch(function (error) {
            // console.log("Error adding record: " + error);
        });
    }

    function deleteRecord(table: string, column: string, value: string) {

        AsyncRequest.request({
            command: "sql_command",
            sql: `DELETE`,
            table:table,
            column:column,
            value:value
        }).then(function (results) {
            // console.log("Record inserted successfully");
            // Handle success if needed
        }).catch(function (error) {
            console.log("Error adding record: " + error);
        });
    }

    function request(request) {
        return new Promise(function (resolve, reject) {
            var requestId = Backend.request(request || {});

            pendingRequests[requestId] = {
                resolve: resolve,
                reject: reject
            };
        });
    }

    Component.onCompleted: {
        Backend.responseReady.connect(function (requestId, result) {
            // console.log('recieved respons:', requestId, JSON.stringify(result));
            if (pendingRequests[requestId]) {
                pendingRequests[requestId].resolve(result);
                delete pendingRequests[requestId];
            }
        });

        Backend.errorOccurred.connect(function (requestId, error) {
            console.log('error respons:', requestId, JSON.stringify(result));
            if (pendingRequests[requestId]) {
                pendingRequests[requestId].reject(error);
                delete pendingRequests[requestId];
            }
        });
    }
}
