FROM eclipse-temurin:17-jdk-jammy

RUN useradd -ms /bin/bash runner
WORKDIR /workspace
RUN chmod 777 /workspace
USER runner

CMD ["sh", "-c", "javac Main.java && java -cp /workspace Main"]
