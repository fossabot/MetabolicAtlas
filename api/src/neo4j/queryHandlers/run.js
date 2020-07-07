import driver from '../driver';

const runStatement = async (statement) => {
  const session = driver.session();

  let error;

  try {
    await session.run(statement);
  } catch (e) {
    error = e;
  } finally {
    await session.close();
  }

  if (error) {
    throw error;
  }
};

export default runStatement;
