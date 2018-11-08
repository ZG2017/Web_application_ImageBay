package ece1779.loadgenerator;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLConnection;
import java.util.Date;
import java.util.Timer;

public class Worker extends Thread {
	private final String CrLf = "\r\n";

	private LoadGenerator generator;
	private int id;
	private String userid;
	private String password;
	
	public Worker(LoadGenerator generator, int id, String userid, String password) {
		this.generator = generator;
		this.id = id;
		this.userid = userid;
		this.password = password;
	}
	
	public void run() {
		while(true) {
			try {
				String resourceDir = "images/";
				
				URL dirURL = getClass().getResource(resourceDir);

				if (dirURL == null)
					return;
				
				String [] files = new File(dirURL.toURI()).list();
				
				for (int x=0; files != null && x < files.length; x++) {
					if (id > generator.getNumActive())
						return;
					Date startTime = new Date();
					postFile(resourceDir,files[x]);
					Date stopTime = new Date();
					long latency = stopTime.getTime() - startTime.getTime();
					generator.reportLatency(latency);
					generator.log("Worker " + id + " Upload " + files[x] + " Reponse Time = " + latency);
				}
			} catch (URISyntaxException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} 
		}
	}
	
	 private void postFile(String dir, String filename) {
	        URLConnection conn = null;
	        OutputStream os = null;
	        InputStream is = null;

	        try {
	            URL url = new URL(generator.getServerURL());

	            conn = url.openConnection();
	            conn.setDoOutput(true);

	            String postData = "";

	            InputStream imgIs = getClass().getResourceAsStream(dir + filename);
	            byte[] imgData = new byte[imgIs.available()];
	            imgIs.read(imgData);

	            String message0 = "";
	            message0 += "-----------------------------4664151417711" + CrLf;
	            message0 += "Content-Disposition: form-data; name=\"userID\""
	                    + CrLf + CrLf;
	            message0 += userid + CrLf;
	           
	            String message1 = "";
	            message1 += "-----------------------------4664151417711" + CrLf;
	            message1 += "Content-Disposition: form-data; name=\"password\""
	                    + CrLf + CrLf;
	            message1 += password + CrLf;
	           
	            
	            
	            String message2 = "";
	            message2 += "-----------------------------4664151417711" + CrLf;
	            message2 += "Content-Disposition: form-data; name=\"uploadedfile\"; filename=\"" + filename  + "\""
	                    + CrLf;
	            message2 += "Content-Type: image/gif" + CrLf;
	            message2 += CrLf;

	            // the image is sent between the messages in the multipart message.

	            String message3 = "";
	            message3 += CrLf + "-----------------------------4664151417711--"
	                    + CrLf;

	            conn.setRequestProperty("Content-Type",
	                    "multipart/form-data; boundary=---------------------------4664151417711");
	            // might not need to specify the content-length when sending chunked
	            // data.
	            conn.setRequestProperty("Content-Length", String.valueOf((message0.length() +
	            		message1.length() + message2.length() + message3.length() + imgData.length)));

	            os = conn.getOutputStream();

	            os.write(message0.getBytes());

	            os.write(message1.getBytes());

	            os.write(message2.getBytes());
	            
	            
	            // SEND THE IMAGE
	            int index = 0;
	            int size = 1024;
	            do {
	                if ((index + size) > imgData.length) {
	                    size = imgData.length - index;
	                }
	                os.write(imgData, index, size);
	                index += size;
	            } while (index < imgData.length);

	            os.write(message3.getBytes());
	            os.flush();

	            is = conn.getInputStream();

	            char buff = 512;
	            int len;
	            byte[] data = new byte[buff];
	            do {
	                len = is.read(data);
	            } while (len > 0);

	        } catch (Exception e) {
	            e.printStackTrace();
	        } finally {
	            try {
	                os.close();
	            } catch (Exception e) {
	            }
	            try {
	                is.close();
	            } catch (Exception e) {
	            }
	            try {

	            } catch (Exception e) {
	            }
	        }
	    }

	
}
