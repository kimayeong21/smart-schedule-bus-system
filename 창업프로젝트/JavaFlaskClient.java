import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONArray;
import org.json.JSONObject;

public class JavaFlaskClient extends JFrame {
    private static final String BASE_URL = "http://localhost:5000/api";
    private JTextArea outputArea;
    private Integer currentUserId = null;
    private JPanel centerPanel;  // 중앙 패널을 교체 가능하게

    public JavaFlaskClient() {
        setTitle("🚌 청주 버스 + 일정 관리 클라이언트");
        setSize(900, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        JButton btnRegister = new JButton("📝 회원가입");
        JButton btnLogin = new JButton("🔑 로그인");
        JButton btnSchedules = new JButton("📅 일정 조회");
        JButton btnAddSchedule = new JButton("➕ 일정 추가");
        JButton btnBusStops = new JButton("🚌 버스번호 조회");

        JPanel topPanel = new JPanel();
        topPanel.add(btnRegister);
        topPanel.add(btnLogin);
        topPanel.add(btnSchedules);
        topPanel.add(btnAddSchedule);
        topPanel.add(btnBusStops);
        add(topPanel, BorderLayout.NORTH);

        // 중앙 패널 (동적으로 교체)
        centerPanel = new JPanel(new BorderLayout());
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        centerPanel.add(new JScrollPane(outputArea), BorderLayout.CENTER);
        add(centerPanel, BorderLayout.CENTER);

        btnRegister.addActionListener(e -> signup());
        btnLogin.addActionListener(e -> login());
        btnSchedules.addActionListener(e -> getSchedules());
        btnAddSchedule.addActionListener(e -> addSchedule());
        btnBusStops.addActionListener(e -> getBusStops());
    }

    // ---------------- Flask API 호출 ----------------
    private String callApi(String path, String method, String body) throws Exception {
        URL url = new URL(BASE_URL + path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod(method);
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        if (body != null) {
            try (OutputStream os = conn.getOutputStream()) {
                os.write(body.getBytes());
            }
        }

        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) sb.append(line);
        return sb.toString();
    }

    // ---------------- 회원가입 ----------------
    private void signup() {
        String username = JOptionPane.showInputDialog("아이디 입력:");
        String password = JOptionPane.showInputDialog("비밀번호 입력:");
        String name = JOptionPane.showInputDialog("이름 입력:");

        try {
            String body = String.format("{\"username\":\"%s\",\"password\":\"%s\",\"name\":\"%s\"}",
                    username, password, name);
            String res = callApi("/signup", "POST", body);
            outputArea.setText("회원가입 결과:\n" + res);
        } catch (Exception e) {
            outputArea.setText("❌ 오류: " + e.getMessage());
        }
    }

    // ---------------- 로그인 ----------------
    private void login() {
        String username = JOptionPane.showInputDialog("아이디 입력:");
        String password = JOptionPane.showInputDialog("비밀번호 입력:");

        try {
            String body = String.format("{\"username\":\"%s\",\"password\":\"%s\"}", username, password);
            String res = callApi("/login", "POST", body);

            JSONObject obj = new JSONObject(res);
            if (obj.getBoolean("success")) {
                currentUserId = obj.getInt("id");
                outputArea.setText("✅ 로그인 성공! 사용자: " + obj.getString("name"));
            } else {
                outputArea.setText("❌ 로그인 실패: " + obj.optString("error"));
            }
        } catch (Exception e) {
            outputArea.setText("❌ 오류: " + e.getMessage());
        }
    }

    // ---------------- 일정 조회 ----------------
    private void getSchedules() {
        if (currentUserId == null) {
            outputArea.setText("❌ 먼저 로그인 해주세요");
            return;
        }
        try {
            String res = callApi("/schedules/" + currentUserId, "GET", null);
            outputArea.setText("일정 목록:\n" + res);
        } catch (Exception e) {
            outputArea.setText("❌ 오류: " + e.getMessage());
        }
    }

    // ---------------- 일정 추가 ----------------
    private void addSchedule() {
        if (currentUserId == null) {
            outputArea.setText("❌ 먼저 로그인 해주세요");
            return;
        }

        String title = JOptionPane.showInputDialog("일정 제목:");
        String desc = JOptionPane.showInputDialog("설명:");
        String start = JOptionPane.showInputDialog("시작 시간 (2025-09-24 10:00)");
        String end = JOptionPane.showInputDialog("종료 시간 (2025-09-24 12:00)");

        try {
            String body = String.format("{\"user_id\":%d,\"title\":\"%s\",\"description\":\"%s\",\"start_time\":\"%s\",\"end_time\":\"%s\"}",
                    currentUserId, title, desc, start, end);
            String res = callApi("/schedules", "POST", body);
            outputArea.setText("일정 추가 결과:\n" + res);
        } catch (Exception e) {
            outputArea.setText("❌ 오류: " + e.getMessage());
        }
    }

    // ---------------- 버스 조회 ----------------
    private void getBusStops() {
        String routeNo = JOptionPane.showInputDialog("조회할 버스번호 입력:");
        if (routeNo == null || routeNo.isEmpty()) return;

        try {
            String res = callApi("/bus/route?route_no=" + routeNo, "GET", null);
            JSONObject obj = new JSONObject(res);

            if (!obj.getBoolean("success")) {
                outputArea.setText("❌ 오류: " + obj.getString("error"));
                return;
            }

            JSONArray stops = obj.getJSONArray("stops");

            // JTable 생성
            String[] cols = {"정류장ID", "정류장명", "X좌표", "Y좌표"};
            DefaultTableModel model = new DefaultTableModel(cols, 0);

            for (int i = 0; i < stops.length(); i++) {
                JSONObject stop = stops.getJSONObject(i);
                model.addRow(new Object[]{
                        stop.getString("stop_id"),
                        stop.getString("stop_name"),
                        stop.getDouble("x"),
                        stop.getDouble("y")
                });
            }

            JTable table = new JTable(model);
            table.setRowHeight(25);

            // 중앙 패널 교체
            centerPanel.removeAll();
            centerPanel.add(new JScrollPane(table), BorderLayout.CENTER);
            centerPanel.revalidate();
            centerPanel.repaint();

        } catch (Exception e) {
            outputArea.setText("❌ 오류: " + e.getMessage());
        }
    }

    // ---------------- 실행 ----------------
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new JavaFlaskClient().setVisible(true));
    }
}
