CXX = g++
CXXFLAGS = -std=c++17 -O2 -s -static
LDFLAGS = -lwinhttp -lws2_32 -lcrypt32

TARGET = kraken.exe
SOURCES = agent.cpp

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)
	strip $(TARGET)
	@echo "✅ Kraken agent compiled: $(TARGET)"

clean:
	rm -f $(TARGET)

.PHONY: clean