import QtQuick 2.15


Rectangle {
    id: root
    
    property string filePath:""
    


    color: "#f0f0f0"
    
    Flickable {
        anchors.fill: parent

        contentWidth: Math.max(image.width * image.scale, root.width)
        contentHeight: Math.max(image.height * image.scale, root.height)
        clip: true

        Image {
            id: image

            property real zoom: 0.0
            property real zoomStep: 0.1

            asynchronous: true
            cache: false
            smooth: true
            source: "file:///" + root.filePath
            antialiasing: true
            mipmap: true

            anchors.centerIn: parent
            fillMode: Image.PreserveAspectFit

            transformOrigin: Item.Center
            scale: Math.min(root.width / width, root.height / height, 1) + zoom

        }
    }

    // Mouse zoom
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton

        onWheel: {
            if (wheel.angleDelta.y > 0)
                image.zoom = Number((image.zoom + image.zoomStep).toFixed(1))
            else
                if (image.zoom > 0) image.zoom = Number((image.zoom - image.zoomStep).toFixed(1))

            wheel.accepted=true
        }
    }
    


}