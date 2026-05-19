FROM eclipse-temurin:17-jdk-jammy

RUN useradd -ms /bin/bash runner
WORKDIR /workspace
USER runner

CMD ["sh", "-c", "javac Main.java && java -cp /workspace Main"]
