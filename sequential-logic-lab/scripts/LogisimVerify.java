import com.cburch.logisim.Main;
import com.cburch.logisim.circuit.*;
import com.cburch.logisim.comp.*;
import com.cburch.logisim.data.*;
import com.cburch.logisim.file.*;
import com.cburch.logisim.instance.StdAttr;
import com.cburch.logisim.proj.Project;
import com.cburch.logisim.std.wiring.Pin;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

/** Runs the actual Logisim-evolution propagation engine, retaining state between vectors. */
public class LogisimVerify {
    static void render(Circuit c, CircuitState state, Path path) throws Exception {
        Bounds b = c.getBounds().expand(75);
        int scale = 2;
        BufferedImage img = new BufferedImage(b.getWidth()*scale, b.getHeight()*scale, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = img.createGraphics();
        g.setColor(Color.WHITE); g.fillRect(0,0,img.getWidth(),img.getHeight());
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.scale(scale,scale); g.translate(-b.getX(),-b.getY());
        ComponentDrawContext ctx = new ComponentDrawContext(null,c,state,g,g);
        ctx.setShowState(true); ctx.setShowColor(true);
        c.draw(ctx,null);
        g.dispose(); Files.createDirectories(path.toAbsolutePath().getParent());
        ImageIO.write(img,"png",path.toFile());
    }
    public static void main(String[] args) {
        try { run(args); } catch(Throwable failure) { failure.printStackTrace(); System.exit(1); }
    }
    static void run(String[] args) throws Exception {
        Main.headless = true;
        LogisimFile file = new Loader(null).openLogisimFile(new File(args[0]));
        Project project = new Project(file);
        Circuit circuit = file.getMainCircuit();
        CircuitState state = CircuitState.createRootState(project,circuit,Thread.currentThread());
        Map<String,com.cburch.logisim.comp.Component> pins = new LinkedHashMap<>();
        for (var c : circuit.getNonWires()) {
            String name=c.getFactory().getName();
            StringJoiner ports=new StringJoiner(";");
            for(var end:c.getEnds())ports.add(end.getLocation().toString());
            System.out.println("COMP "+name+" "+c.getLocation()+" PORTS "+ports);
            if(c.getFactory() instanceof Pin) pins.put(c.getAttributeSet().getValue(StdAttr.LABEL), c);
        }
        if(args.length<2) { System.exit(0); }
        var lines = Files.readAllLines(Path.of(args[1]));
        String[] headers=lines.get(0).split(","); int passed=0;
        for(int i=1;i<lines.size();i++) {
            String line=lines.get(i).trim(); if(line.isEmpty()||line.startsWith("#"))continue;
            String[] values=line.split(",");
            for(int k=0;k<headers.length;k++) {
                var c=pins.get(headers[k]); if(c==null)continue;
                Pin pin=(Pin)c.getFactory(); var inst=state.getInstanceState(c);
                if(pin.isInputPin(inst.getInstance()) && !values[k].equals("-")) {
                    pin.driveInputPin(inst,values[k].equals("1")?Value.TRUE:Value.FALSE);
                    state.markComponentAsDirty(c);
                }
            }
            state.getPropagator().propagate();
            if(state.getPropagator().isOscillating()) throw new AssertionError("Oscillation at row "+i);
            StringJoiner actual=new StringJoiner(",");
            for(int k=0;k<headers.length;k++) {
                var c=pins.get(headers[k]); if(c==null){actual.add(values[k]);continue;}
                Pin pin=(Pin)c.getFactory();var inst=state.getInstanceState(c);
                String v=pin.getValue(inst).toBinaryString(); actual.add(v);
                if(!pin.isInputPin(inst.getInstance()) && !values[k].equals("-") && !values[k].equals(v))
                    throw new AssertionError("Row "+i+" "+headers[k]+": expected="+values[k]+" actual="+v);
            }
            System.out.println("PASS row="+i+" "+actual); passed++;
            if(args.length>2 && i<=2)render(circuit,state,Path.of(args[2]+"_state"+i+".png"));
        }
        if(args.length>2)render(circuit,state,Path.of(args[2]+"_schematic.png"));
        System.out.println("LOGISIM PASS: "+passed+" sequential vectors; no oscillation");
        System.exit(0);
    }
}
