package ece1779.loadgenerator;

import javax.swing.*;
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;
/** 
    This class demonstrates the basics of setting up a Java Swing GUI uisng the
    BorderLayout. You should be able to use this program to drop in other
    components when building a GUI 
*/
public class GUI extends JFrame{
    
	
	public LoadGenerator generator;
	
	// Initialize all swing objects.

    
    
    
    private JTextArea statusBox = new JTextArea(20,20);
    private JScrollPane scrollBox = new JScrollPane(statusBox);
    
    
    // Buttons some there is something to put in the panels
    private JButton startWorker = new JButton("Start Worker");
    private JButton stopWorker = new JButton("Stop Worker");

    private JLabel numWorkersLabel = new JLabel("Workers");
    private JTextField numWorkers = new JTextField(6);
    
    private JLabel avgLatencyLabel = new JLabel("Avg. Latency");
    private JTextField avgLatency = new JTextField(6);

    private JLabel throughputLabel = new JLabel("Throughput");
    private JTextField throughput = new JTextField(6);

   
    // Menu
    private JMenuBar mb = new JMenuBar(); // Menubar
    private JMenu mnuFile = new JMenu("File"); // File Entry on Menu bar
    private JMenuItem mnuItemQuit = new JMenuItem("Quit"); // Quit sub item
    private JMenu mnuHelp = new JMenu("Help"); // Help Menu entry
    private JMenuItem mnuItemAbout = new JMenuItem("About"); // About Entry

    /** Constructor for the GUI */
    public GUI(LoadGenerator gen){
  
    		super("Basic GUI");
    		
    		this.generator = gen;
    		
    		// Set menubar
        setJMenuBar(mb);
        
        //Build Menus
        mnuFile.add(mnuItemQuit);  // Create Quit line
        mb.add(mnuFile);        // Add Menu items to form

        
        JPanel pnlNorth = new JPanel(); // North quadrant     
        pnlNorth.setLayout(new BorderLayout());
        pnlNorth.add(scrollBox);
        
        
        JPanel pnlButtonStart = new JPanel(); // East quadrant
        pnlButtonStart.add(startWorker);
        
        
        JPanel pnlButtonStop = new JPanel(); // East quadrant
        pnlButtonStop.add(stopWorker);
        
        JPanel pnlButtons = new JPanel(); // East quadrant
        pnlButtons.setLayout(new BorderLayout());
        pnlButtons.add(pnlButtonStart, BorderLayout.NORTH);
        pnlButtons.add(pnlButtonStop, BorderLayout.SOUTH);
        
        
        JPanel pnlValueWorkers = new JPanel(); // West quadrant
        pnlValueWorkers.setLayout(new BorderLayout());
        pnlValueWorkers.add(numWorkersLabel,BorderLayout.WEST);
        pnlValueWorkers.add(numWorkers,BorderLayout.EAST);
        
        JPanel pnlValueLatencies = new JPanel(); // West quadrant
        pnlValueLatencies.setLayout(new BorderLayout());
        pnlValueLatencies.add(avgLatencyLabel,BorderLayout.WEST);
        pnlValueLatencies.add(avgLatency,BorderLayout.EAST);
        
        JPanel pnlThroughput = new JPanel(); // West quadrant
        pnlThroughput.setLayout(new BorderLayout());
        pnlThroughput.add(throughputLabel,BorderLayout.WEST);
        pnlThroughput.add(throughput,BorderLayout.EAST);
       
        
        JPanel pnlValues = new JPanel(); // West quadrant
        pnlValues.setLayout(new BorderLayout());
        pnlValues.add(pnlValueWorkers,BorderLayout.NORTH);
        pnlValues.add(pnlValueLatencies,BorderLayout.CENTER);
        pnlValues.add(pnlThroughput,BorderLayout.SOUTH);
         
        
        JPanel pnlSouth = new JPanel(); // South quadrant
  //      pnlSouth.setLayout(new BorderLayout());
        pnlSouth.add(pnlButtons);
        pnlSouth.add(pnlValues);
        
        startWorker.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                generator.addWorker();
            }
        });
        
        stopWorker.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                generator.stopWorker();
            }
        });
        
        
        // Setup Main Frame
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(pnlNorth, BorderLayout.NORTH);
        getContentPane().add(pnlSouth, BorderLayout.SOUTH);
        
        // Allows the Swing App to be closed
        addWindowListener(new ListenCloseWdw());
        
        //Add Menu listener
        mnuItemQuit.addActionListener(new ListenMenuQuit());

        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        //pack(); //Adjusts panel to components for display

        
		setTitle("Load Generator");
		setSize(800,500); // default size is 0,0
//		setLocation(200,200); // default is 0,0 (top left corner)

    }
    
    public class ListenMenuQuit implements ActionListener{
        public void actionPerformed(ActionEvent e){
            System.exit(0);         
        }
    }
    
    public class ListenCloseWdw extends WindowAdapter{
        public void windowClosing(WindowEvent e){
            System.exit(0);         
        }
    }

	public void log(String msg) {
		int row = statusBox.getRows();
		
		statusBox.append(msg + "\n");
	}

	public void refresh() {
		numWorkers.setText("" + generator.getNumActive());
		avgLatency.setText("" + generator.getLatency());
		throughput.setText("" + generator.getThroughput());
	}

	
    
    
}

