package com.example.redycler

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.util.Log
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.util.*

class ConnectThread(device: BluetoothDevice) : Thread() {

    private val TAG = "BLE_CONNECT"
    private val RPI_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    private val mmInStream: InputStream?
    private val mmOutStream: OutputStream?

    private val mmSocket: BluetoothSocket? by lazy(LazyThreadSafetyMode.NONE) {
        device.createRfcommSocketToServiceRecord(RPI_UUID)
    }

    init {
        var tmpIn: InputStream? = null
        var tmpOut: OutputStream? = null

        // Get the input and output streams, using temp objects because
        // member streams are final
        try {
            tmpIn = mmSocket?.inputStream
            tmpOut = mmSocket?.outputStream
        } catch (e: IOException) {
        }
        mmInStream = tmpIn
        mmOutStream = tmpOut
    }

    public override fun run() {
        // Cancel discovery because it otherwise slows down the connection.
        val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
        bluetoothAdapter?.cancelDiscovery()

        mmSocket?.let { socket ->
            // Connect to the remote device through the socket. This call blocks
            // until it succeeds or throws an exception.
            socket.connect()

            // The connection attempt succeeded. Perform work associated with
            // the connection in a separate thread.
            Log.d(TAG, "Socket connected")

        }
    }

    /* Call this from the main activity to send data to the remote device */
    fun write(selection: Int) {
        try {
            mmOutStream?.write(selection)
        } catch (e: IOException) {
            Log.e(TAG, e.toString())
        }
    }

    // Closes the client socket and causes the thread to finish.
    fun cancel() {
        try {
            mmSocket?.close()
        } catch (e: IOException) {
            Log.e(TAG, "Could not close the client socket", e)
        }
    }
}